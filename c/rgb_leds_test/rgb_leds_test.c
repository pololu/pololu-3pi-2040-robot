// This example shows how to control the six RGB LEDs on the
// Pololu 3pi+ 2040 Robot.

#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

rgb_color colors[6];

int main()
{
  stdio_init_all();
  rgb_leds_init();

  while (true)
  {
    colors[0] = (rgb_color){ 0x40, 0x00, 0x00 };  // red
    colors[1] = (rgb_color){ 0x00, 0x40, 0x00 };  // green
    colors[2] = (rgb_color){ 0x00, 0x00, 0x40 };  // blue

    colors[3] = (rgb_color){ 0x40, 0x00, 0x00 };  // red
    colors[4] = (rgb_color){ 0x00, 0x40, 0x00 };  // green

    // blue, blinking on and off
    if (time_us_32() >> 18 & 1)
    {
      colors[5] = (rgb_color){ 0, 0, 0 };  // off
    }
    else
    {
      colors[5] = (rgb_color){ 0x00, 0x00, 0x40 };  // blue
    }

    // This command sends the colors to the RGB LEDs, making them update.
    // The third parameter below is a brightness value from 1 to 31.
    rgb_leds_write(colors, 6, 2);
  }
}
