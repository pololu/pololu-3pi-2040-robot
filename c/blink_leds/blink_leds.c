// This example shows how to blink the yellow LED and the six RGB LEDs on the
// Pololu 3p+ 2040 Robot.

#include <pico/stdlib.h>
#include <pololu_3pi_plus_2040_robot.h>

uint32_t count;

int main()
{
  stdio_init_all();
  rgb_init();

  while (true)
  {
    // Blink the yellow LED with blocking code.
    led_yellow(0);
    sleep_ms(250);
    led_yellow(1);
    sleep_ms(250);

    // It is also possible to blink the yellow LED without delays like this:
    //   led_yellow(time_us_32() >> 18 & 1);

    // Blink the six RGB LEDs in sequence, with different colors.
    const uint8_t v = 128;
    count++;
    if (count >= 18) { count = 0; }
    rgb_start_frame();
    rgb_write((count == 0) * v, (count == 6) * v, (count == 12) * v, 1);
    rgb_write((count == 1) * v, (count == 7) * v, (count == 13) * v, 1);
    rgb_write((count == 2) * v, (count == 8) * v, (count == 14) * v, 1);
    rgb_write((count == 3) * v, (count == 9) * v, (count == 15) * v, 1);
    rgb_write((count == 4) * v, (count == 10) * v, (count == 16) * v, 1);
    rgb_write((count == 5) * v, (count == 11) * v, (count == 17) * v, 1);
    rgb_end_frame(6);
  }
}
