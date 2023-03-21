// This example shows how to read the buttons on the Pololu 3p+ 2040 Robot and
// simultaneously blink the yellow LED, blink the RGB LEDs, print to the USB
// serial port, and display info on the OLED.

#include <string.h>
#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

char last_report[64];

int main()
{
  stdio_init_all();
  rgb_leds_init();
  sh1106_init();

  while (true)
  {
    // Blink the yellow LED.
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

    bool a_pressed = button_a_is_pressed();
    bool b_pressed = button_b_is_pressed();
    bool c_pressed = button_c_is_pressed();

    // Show the button states on the OLED.
    uint8_t page_data[128] = { 0 };
    if (a_pressed) { memset(page_data + 2, 0xFF, 40); }
    if (b_pressed) { memset(page_data + 44, 0xFF, 40); }
    if (c_pressed) { memset(page_data + 86, 0xFF, 40); }
    sh1106_transfer_start();
    for (uint8_t page = 0; page < 8; page++)
    {
      if (page == 7)
      {
        memset(page_data + 2, 0xFF, 40);
        memset(page_data + 44, 0xFF, 40);
        memset(page_data + 86, 0xFF, 40);
      }
      sh1106_write_page(page, 0, page_data, 128);
    }
    sh1106_transfer_end();

    // Show the button states on the RGB LEDs.
    rgb_color colors[6] = { 0 };
    if (a_pressed) { colors[0] = colors[5] = (rgb_color){ 80, 0, 0 }; }
    if (b_pressed) { colors[1] = colors[4] = (rgb_color){ 0, 80, 0 }; }
    if (c_pressed) { colors[2] = colors[3] = (rgb_color){ 0, 0, 80 }; }
    rgb_leds_write(colors, 6, 2);
  }
}
