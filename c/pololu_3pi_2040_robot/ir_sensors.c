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

uint16_t bump_sensor_left, bump_sensor_right, line_sensors[5];

// TODO: uint16_t line_sensors_cal_min[5] = { 1024, 1024, 1024, 1024, 1024 };
// TODO: uint16_t line_sensors_cal_max[5] = { 0, 0, 0, 0, 0 };

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

  sleep_us(10);

  pio_sm_config cfg = qtr_sensor_counter_program_get_default_config(counter_offset);
  sm_config_set_clkdiv_int_frac(&cfg, 15, 160);   // 125/(15+160/256) = 8 MHz
  // sm_config_set_clkdiv_int_frac(&cfg, 31, 64);   // 125/(31+64/256) = 4 MHz
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

  for (uint8_t i = 0; i < 5; i++) { line_sensors[i] = output[i + 2]; }
}

void bump_sensors_start_read()
{
  gpio_init(IR_EMITTER_LINE);

  gpio_init(IR_EMITTER_BUMP);
  gpio_put(IR_EMITTER_BUMP, 1);
  gpio_set_dir(IR_EMITTER_BUMP, GPIO_OUT);

  sleep_us(200);

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

  bump_sensor_left = output[0];
  bump_sensor_right = output[1];
}
