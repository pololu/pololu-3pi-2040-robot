// TODO

#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_plus_2040_robot.h>

int main()
{
  stdio_init_all();

  while (1)
  {
    if (button_a_is_pressed())
    {
      printf("Calling ir_sensors_run...\n");
      ir_sensors_run();
      sleep_ms(20);
      while (button_a_is_pressed());
      sleep_ms(20);
    }

    yellow_led(time_us_32() >> 18 & 1);
  }
}
