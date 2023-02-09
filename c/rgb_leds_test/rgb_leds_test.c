// This example shows how to control the six RGB LEDs on the
// Pololu 3p+ 2040 Robot.

#include <pico/stdlib.h>
#include <pololu_3pi_plus_2040_robot.h>

int main()
{
  stdio_init_all();
  rgb_leds_init();

  while (true)
  {
    rgb_leds_start_frame();

    rgb_leds_write(0x80, 0x00, 0x00, 1);  // red
    rgb_leds_write(0x00, 0x80, 0x00, 1);  // green
    rgb_leds_write(0x00, 0x00, 0x80, 1);  // blue
    rgb_leds_write(0x80, 0x00, 0x00, 1);  // red
    rgb_leds_write(0x00, 0x80, 0x00, 1);  // green

    // blue, blinking on and off
    if (time_us_32() >> 18 & 1)
    {
      rgb_leds_write(0, 0, 0, 1);  // off
    }
    else
    {
      rgb_leds_write(0x00, 0x00, 0x80, 1);  // blue
    }

    // This makes all the LEDs use their new colors immediately.  It is not
    // strictly necessary for this demo.
    rgb_leds_end_frame(6);
  }
}
