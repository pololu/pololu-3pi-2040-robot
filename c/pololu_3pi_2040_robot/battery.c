#include <pico/stdlib.h>
#include <hardware/adc.h>
#include <pololu_3pi_2040_robot.h>

uint16_t battery_get_level_millivolts()
{
  if (!(adc_hw->cs & ADC_CS_EN_BITS)) { adc_init(); }
  adc_select_input(0);
  adc_gpio_init(26);
  return adc_read() * (11 * 3300) / 4096;
}
