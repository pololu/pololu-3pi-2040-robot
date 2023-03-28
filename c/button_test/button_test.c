// This example shows how to read the buttons on the Pololu 3p+ 2040 Robot and
// simultaneously blink the yellow LED, blink the RGB LEDs, print to the USB
// serial port, and display info on the OLED.

#include <string.h>
#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

char last_report[64];

button button_a;
button button_b;
button button_c;

uint32_t cursor_x;

void oled_print(const char * str)
{
  display_set_font(font_8x16);
  cursor_x = display_text(str, cursor_x, 48, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);
  if (cursor_x >= DISPLAY_WIDTH)
  {
    // TODO: display_fill_rect(0, 48, DISPLAY_WIDTH, 8, COLOR_BLACK | DISPLAY_NOW);
    memset(display_buffer + 6 * DISPLAY_WIDTH, 0, 2 * DISPLAY_WIDTH);
    display_show();
    cursor_x = 0;
  }
}

int main()
{
  stdio_init_all();
  display_init();

  button_a_init(&button_a);
  button_b_init(&button_b);
  button_c_init(&button_c);

  button_a.debounce_us = 500000;

  display_text("A:", 0, 0, 1);
  display_text("B:", 0, 8, 1);
  display_text("C:", 0, 16, 1);

  display_text("Debounced output", 0, 28, 1);
  display_text("with A at 500ms:", 0, 36, 1);
  display_show();

  while (true)
  {
    bool a_pressed = button_a_is_pressed();
    bool b_pressed = button_b_is_pressed();
    bool c_pressed = button_c_is_pressed();

    // Show the button states on the OLED.
    display_set_font(font_8x8);
    display_text(a_pressed ? "1" : "0", 24, 0, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);
    display_text(b_pressed ? "1" : "0", 24, 8, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);
    display_text(c_pressed ? "1" : "0", 24, 16, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);
    if (button_check(&button_a) == 1) { oled_print("A"); }
    if (button_check(&button_b) == 1) { oled_print("B"); }
    if (button_check(&button_c) == 1) { oled_print("C"); }
  }
}
