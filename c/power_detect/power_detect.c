#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

int main()
{
  stdio_init_all();
  while (1)
  {
    uint16_t battery_level = battery_get_level_millivolts();
    printf("Battery: %u mV\n", battery_level);
    sleep_ms(1000);
  }
}

