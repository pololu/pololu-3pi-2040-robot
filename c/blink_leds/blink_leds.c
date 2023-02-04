// This example shows how to blink the yellow LED and the six RGB LEDs on the
// Pololu 3p+ 2040 Robot.

#include <pico/stdlib.h>
#include <pololu_3pi_plus_2040_robot.h>

int main()
{
  stdio_init_all();
  rgb_leds_init();

  while (true)
  {
    yellow_led(0);

    rgb_leds_start_frame();
    rgb_leds_write(0x80, 0x00, 0x00, 1);  // red
    rgb_leds_write(0x00, 0x80, 0x00, 1);  // green
    rgb_leds_write(0x00, 0x00, 0x80, 1);  // blue
    rgb_leds_write(0x80, 0x00, 0x00, 1);  // red
    rgb_leds_write(0x00, 0x80, 0x00, 1);  // green
    rgb_leds_write(0x00, 0x00, 0x80, 1);  // blue
    rgb_leds_end_frame(6);

    sleep_ms(250);

    yellow_led(1);

    rgb_leds_start_frame();
    for (unsigned int i = 0; i < 6; i++)
    {
      rgb_leds_write(0x80, 0x40, 0x00, 1);  // yellow
    }
    rgb_leds_end_frame(6);

    sleep_ms(250);

    // It is also possible to blink the yellow LED without delays like this:
    //   yellow_led(time_us_32() >> 18 & 1);
  }
}
