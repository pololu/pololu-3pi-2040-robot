// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <ir_sensors.h>
#include <string.h>
#include <pico/stdlib.h>
#include <hardware/pio.h>

#include <qtr_sensor_counter.pio.h>

#define IR_PIO pio1
#define IR_FUNC GPIO_FUNC_PIO1

#define IR_EMITTER_BUMP 23
#define IR_EMITTER_LINE 26

#define TIMEOUT 1024

static uint8_t counter_sm = 0xFF;
static uint8_t counter_offset;

#define STATE_DONE 0
#define STATE_READ_LINE 1
#define STATE_READ_BUMP 2
uint8_t state;

uint16_t bump_sensors[2];
uint16_t bump_sensors_threshold_min[2] = { 1025, 1025 };
uint16_t bump_sensors_threshold_max[2] = { 1025, 1025 };
bool bump_sensors_pressed[2];

uint16_t line_sensors[5];
uint16_t line_sensors_cal_min[5] = { 1025, 1025, 1025, 1025, 1025 };
uint16_t line_sensors_cal_max[5] = { 0, 0, 0, 0, 0 };
uint16_t line_sensors_calibrated[5];

static void ir_sensors_start_read()
{
  if (counter_sm == 0xFF)
  {
    counter_offset = pio_add_program(IR_PIO, &qtr_sensor_counter_program);
    counter_sm = pio_claim_unused_sm(IR_PIO, true);
  }

  const uint32_t mask = 0x7F << 16;

  // Disable sensor pull-ups and pull-downs.
  gpio_disable_pulls(16);
  gpio_disable_pulls(17);
  gpio_disable_pulls(18);
  gpio_disable_pulls(19);
  gpio_disable_pulls(20);
  gpio_disable_pulls(21);
  gpio_disable_pulls(22);

  // Tell the PIO to drive its lines high.
  pio_sm_set_pins_with_mask(IR_PIO, counter_sm, mask, mask);
  pio_sm_set_pindirs_with_mask(IR_PIO, counter_sm, mask, mask);
  gpio_set_function(16, IR_FUNC);
  gpio_set_function(17, IR_FUNC);
  gpio_set_function(18, IR_FUNC);
  gpio_set_function(19, IR_FUNC);
  gpio_set_function(20, IR_FUNC);
  gpio_set_function(21, IR_FUNC);
  gpio_set_function(22, IR_FUNC);

  sleep_us(32);

  pio_sm_config cfg = qtr_sensor_counter_program_get_default_config(counter_offset);
  sm_config_set_clkdiv_int_frac(&cfg, 15, 160);   // 125/(15+160/256) = 8 MHz
  sm_config_set_in_pins(&cfg, 16);
  sm_config_set_out_pins(&cfg, 16, 7);
  sm_config_set_fifo_join(&cfg, PIO_FIFO_JOIN_RX);
  sm_config_set_in_shift(&cfg, false, true, 23);
  pio_sm_init(IR_PIO, counter_sm, counter_offset, &cfg);

  pio_sm_clear_fifos(IR_PIO, counter_sm);
  pio_sm_restart(IR_PIO, counter_sm);

  // Set the counter (y) to 1023 (10 ones).
  pio_sm_exec_wait_blocking(IR_PIO, counter_sm, 0xA0EB);  // mov osr, !null
  pio_sm_exec_wait_blocking(IR_PIO, counter_sm, 0x604A);  // out y, 10

  pio_sm_exec_wait_blocking(IR_PIO, counter_sm, 0xA0E3);  // mov osr, null

  pio_sm_set_enabled(IR_PIO, counter_sm, true);
}

// Finish a reading that was earlier initiated by ir_sensors_start_read.
static void ir_sensors_read(uint16_t * output)
{
  for (uint8_t i = 0; i < 7; i++) { output[i] = TIMEOUT; }

  uint8_t last_state = 0xFF;
  while (1)
  {
    uint32_t data = pio_sm_get_blocking(IR_PIO, counter_sm);
    //printf("IR %08lx us: %08lx\n", time_us_32(), data);
    if (data == 0xFFFFFFFF) { break; }

    uint16_t time_left = data & 0xFFFF;
    uint8_t state = data >> 16 & 0x7F;
    uint8_t new_zeros = last_state & ~state;
    if (new_zeros & (1 << 0)) { output[0] = TIMEOUT - time_left; }
    if (new_zeros & (1 << 1)) { output[1] = TIMEOUT - time_left; }
    if (new_zeros & (1 << 2)) { output[2] = TIMEOUT - time_left; }
    if (new_zeros & (1 << 3)) { output[3] = TIMEOUT - time_left; }
    if (new_zeros & (1 << 4)) { output[4] = TIMEOUT - time_left; }
    if (new_zeros & (1 << 5)) { output[5] = TIMEOUT - time_left; }
    if (new_zeros & (1 << 6)) { output[6] = TIMEOUT - time_left; }
    last_state = state;
  }

  pio_sm_set_enabled(IR_PIO, counter_sm, false);  // stop the state machine
}

void line_sensors_reset_calibration()
{
  for (unsigned int i = 0; i < 5; i++)
  {
    line_sensors_cal_min[i] = 1025;
    line_sensors_cal_max[i] = 0;
  }
}

void line_sensors_calibrate()
{
  uint16_t tmp_min[5] = { 1025, 1025, 1025, 1025, 1025 };
  uint16_t tmp_max[5] = { 0, 0, 0, 0, };

  for (unsigned int trial = 0; trial < 10; trial++)
  {
    line_sensors_read();
    for (unsigned int i = 0; i < 5; i++)
    {
      if (line_sensors[i] < tmp_min[i]) { tmp_min[i] = line_sensors[i]; }
      if (line_sensors[i] > tmp_max[i]) { tmp_max[i] = line_sensors[i]; }
    }
  }

  // Update the calibration range if all trials indicate it is too narrow.
  for (unsigned int i = 0; i < 5; i++)
  {
    if (tmp_min[i] > line_sensors_cal_max[i])
    {
      line_sensors_cal_max[i] = tmp_min[i];
    }
    if (tmp_max[i] < line_sensors_cal_min[i])
    {
      line_sensors_cal_min[i] = tmp_max[i];
    }
  }
}

void line_sensors_start_read()
{
  gpio_init(IR_EMITTER_BUMP);

  gpio_init(IR_EMITTER_LINE);
  gpio_put(IR_EMITTER_LINE, 1);
  gpio_set_dir(IR_EMITTER_LINE, GPIO_OUT);

  state = STATE_READ_LINE;
  ir_sensors_start_read();
}

void line_sensors_read()
{
  if (state != STATE_READ_LINE) { line_sensors_start_read(); }

  uint16_t output[7];
  ir_sensors_read(output);

  gpio_init(IR_EMITTER_LINE);
  gpio_init(IR_EMITTER_BUMP);
  state = STATE_DONE;

  for (uint8_t i = 0; i < 5; i++) { line_sensors[4 - i] = output[i + 2]; }
}

void line_sensors_read_calibrated()
{
  line_sensors_read();

  for (uint8_t i = 0; i < 5; i++)
  {
    if (line_sensors_cal_min[i] >= line_sensors_cal_max[i] ||
      line_sensors[i] < line_sensors_cal_min[i])
    {
      line_sensors_calibrated[i] = 0;
    }
    else if (line_sensors[i] > line_sensors_cal_max[i])
    {
      line_sensors_calibrated[i] = 1000;
    }
    else
    {
      line_sensors_calibrated[i] = (line_sensors[i] - line_sensors_cal_min[i])
        * 1000 / (line_sensors_cal_max[i] - line_sensors_cal_min[i]);
    }
  }
}

void bump_sensors_reset_calibration()
{
  bump_sensors_threshold_min[0] = 1025;
  bump_sensors_threshold_max[0] = 1025;
  bump_sensors_threshold_min[1] = 1025;
  bump_sensors_threshold_max[1] = 1025;
}

void bump_sensors_calibrate()
{
  const unsigned int count = 50;
  uint32_t sum[2] = { 0, 0 };
  for (unsigned int trial = 0; trial < count; trial++)
  {
    bump_sensors_read();
    sum[0] += bump_sensors[0];
    sum[1] += bump_sensors[1];
  }

  // Set the thresholds to 140% and 160% of the average reading.
  for (uint8_t i = 0; i < 2; i++)
  {
    bump_sensors_threshold_min[i] = (sum[i] * 140) / (count * 100);
    bump_sensors_threshold_max[i] = (sum[i] * 160) / (count * 100);
  }
}

void bump_sensors_start_read()
{
  gpio_init(IR_EMITTER_LINE);

  gpio_init(IR_EMITTER_BUMP);
  gpio_put(IR_EMITTER_BUMP, 1);
  gpio_set_dir(IR_EMITTER_BUMP, GPIO_OUT);

  state = STATE_READ_BUMP;
  ir_sensors_start_read();
}

void bump_sensors_read()
{
  if (state != STATE_READ_BUMP) { bump_sensors_start_read(); }

  uint16_t output[7];
  ir_sensors_read(output);

  gpio_init(IR_EMITTER_LINE);
  gpio_init(IR_EMITTER_BUMP);
  state = STATE_DONE;

  for (uint8_t i = 0; i < 2; i ++)
  {
    bump_sensors[i] = output[1 - i];
    uint16_t threshold = bump_sensors_pressed[i] ?
      bump_sensors_threshold_min[i] : bump_sensors_threshold_max[i];
    bump_sensors_pressed[i] = bump_sensors[i] > threshold;
  }
}

bool bump_sensor_left_is_pressed(void)
{
  return bump_sensors_pressed[0];
}

bool bump_sensor_right_is_pressed(void)
{
  return bump_sensors_pressed[1];
}
