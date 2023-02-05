#include <stdio.h>  // tmphax
#include <string.h>

#include <pico/stdlib.h>
#include <hardware/pio.h>

#include <pololu_3pi_plus_2040_robot.h>
#include <qtr_sensor_counter.pio.h>

#define IR_PIO pio1
#define IR_FUNC GPIO_FUNC_PIO1

static uint8_t counter_sm = 0xFF;
static uint8_t counter_offset;

uint16_t ir_sensor_values[7];

void ir_sensors_run()
{
  if (counter_sm == 0xFF)
  {
    counter_offset = pio_add_program(IR_PIO, &qtr_sensor_counter_program);
    counter_sm = pio_claim_unused_sm(IR_PIO, true);
  }

  // Put the emitters in the desired state.
  bool emitters_on = true;
  gpio_init(26);
  gpio_put(26, emitters_on);
  gpio_set_dir(26, GPIO_OUT);

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
  //sm_config_set_clkdiv_int_frac(&cfg, 15, 160);   // 125/(15+160/256) = 8 MHz
  sm_config_set_clkdiv(&cfg, 25);   // 125/25 = 5 MHz
  sm_config_set_in_pins(&cfg, 16);
  sm_config_set_out_pins(&cfg, 16, 7);
  sm_config_set_fifo_join(&cfg, PIO_FIFO_JOIN_RX);
  sm_config_set_in_shift(&cfg, false, true, 32);
  pio_sm_init(IR_PIO, counter_sm, counter_offset, &cfg);

  pio_sm_clear_fifos(IR_PIO, counter_sm);
  pio_sm_restart(IR_PIO, counter_sm);
  pio_sm_set_enabled(IR_PIO, counter_sm, true);

  memset(ir_sensor_values, 0, sizeof(ir_sensor_values));

  uint8_t last_state = 0xFF;
  while (1)
  {
    uint32_t data = pio_sm_get_blocking(IR_PIO, counter_sm);
    // printf("IR %08lx us: %08lx\n", time_us_32(), value);
    if (data == 0xFFFFFFFF) { break; }

    uint16_t time = data >> 16;
    uint8_t state = data & 0x7F;
    uint8_t new_zeros = last_state & ~state;
    if (new_zeros & (1 << 0)) { ir_sensor_values[0] = time; }
    if (new_zeros & (1 << 1)) { ir_sensor_values[1] = time; }
    if (new_zeros & (1 << 2)) { ir_sensor_values[2] = time; }
    if (new_zeros & (1 << 3)) { ir_sensor_values[3] = time; }
    if (new_zeros & (1 << 4)) { ir_sensor_values[4] = time; }
    if (new_zeros & (1 << 5)) { ir_sensor_values[5] = time; }
    if (new_zeros & (1 << 6)) { ir_sensor_values[6] = time; }
    last_state = state;  // TODO: use &= so we detect the *first* 0 transition?
  }

  pio_sm_set_enabled(IR_PIO, counter_sm, false);  // stop the state machine

  gpio_put(26, 0); // turn off emitters
}
