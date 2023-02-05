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
  sh1106_init();

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

    // Show the button states on the OLED.
    bool a_pressed = button_a_is_pressed();
    bool b_pressed = button_b_is_pressed();
    bool c_pressed = button_c_is_pressed();
    sh1106_transfer_start();
    for (uint8_t page = 0; page < 8; page++)
    {
      if (page == 7) { a_pressed = b_pressed = c_pressed = true; }
      sh1106_start_page_write(page);
      uint8_t x = 0;
      while (x < 2) { x++; }
      while (x < 42) { x++; sh1106_write(a_pressed ? 0xFF : 0x00); }
      while (x < 44) { x++; sh1106_write(0); }
      while (x < 84) { x++; sh1106_write(b_pressed ? 0xFF : 0x00); }
      while (x < 86) { x++; sh1106_write(0); }
      while (x < 126) { x++; sh1106_write(c_pressed ? 0xFF : 0x00); }
    }
    sh1106_transfer_end();
  }
}
