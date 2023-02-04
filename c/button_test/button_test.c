// This example shows how to read the buttons on the Pololu 3p+ 2040 Robot and
// print to the USB serial port.

#include <string.h>
#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_plus_2040_robot.h>

char last_report[64];

int main()
{
  stdio_init_all();
  rgb_leds_init();

  while (true)
  {
    yellow_led(time_us_32() >> 18 & 1);

    // Print the button states to USB if they have changed.
    char report[64];
    sprintf(report, "%c%c%c",
      button_a_is_pressed() ? 'A' : '-',
      button_b_is_pressed() ? 'B' : '-',
      button_c_is_pressed() ? 'C' : '-'
    );
    if (strcmp(last_report, report))
    {
      printf("%s\n", report);
      strcpy(last_report, report);
    }
  }
}
