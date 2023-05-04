// This example shows how to read the buttons on the Pololu 3pi+ 2040 Robot.
// This includes the three pushbuttons on the control board and the two bump
// sensors on the front of the robot, which can be used as buttons.
//
// The bump sensors are calibrated when the program starts running: they should
// not be pressed at that time in order to get an accurate calibration.

#include <string.h>
#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

char last_report[64];

// Pushbuttons on the control board.
button button_a = BUTTON_INIT(button_a_is_pressed);
button button_b = BUTTON_INIT(button_b_is_pressed);
button button_c = BUTTON_INIT(button_c_is_pressed);

// Bump sensors on the front of the robot.
button button_l = BUTTON_INIT(bump_sensor_left_is_pressed);
button button_r = BUTTON_INIT(bump_sensor_right_is_pressed);

uint32_t cursor_x;

void oled_print(const char * str)
{
  display_set_font(font_8x16);
  if (cursor_x >= DISPLAY_WIDTH)
  {
    display_fill_rect(0, 48, DISPLAY_WIDTH, 16, 0 | DISPLAY_NOW);
    cursor_x = 0;
  }
  cursor_x = display_text(str, cursor_x, 48, 1 | DISPLAY_NOW);
}

int main()
{
  stdio_init_all();
  display_init();
  bump_sensors_calibrate();

  // Set the debouncing on button A to 500 ms so it is easy to tell that the
  // debouncing works: if you press button A twice quickly, only one press
  // will register.
  button_a.debounce_us = 500000;

  display_text("A:", 0, 0, 1);
  display_text("B:", 0, 8, 1);
  display_text("C:", 0, 16, 1);
  display_text("L:", 64, 0, 1);
  display_text("R:", 64, 8, 1);

  display_text("Debounced output", 0, 28, 1);
  display_text("with A at 500ms:", 0, 36, 1);
  display_show();

  while (true)
  {
    // Read the buttons.
    bool a_pressed = button_a_is_pressed();
    bool b_pressed = button_b_is_pressed();
    bool c_pressed = button_c_is_pressed();
    bump_sensors_read();

    // Show the button states on the OLED.
    display_set_font(font_8x8);
    display_text(a_pressed ? "1" : "0", 24, 0, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);
    display_text(b_pressed ? "1" : "0", 24, 8, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);
    display_text(c_pressed ? "1" : "0", 24, 16, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);
    display_text(bump_sensors_pressed[0] ? "1" : "0", 88, 0, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);
    display_text(bump_sensors_pressed[1] ? "1" : "0", 88, 8, COLOR_WHITE_ON_BLACK | DISPLAY_NOW);

    // At the bottom of the OLED, print a record of button press events.
    if (button_check(&button_a) == 1) { oled_print("A"); }
    if (button_check(&button_b) == 1) { oled_print("B"); }
    if (button_check(&button_c) == 1) { oled_print("C"); }
    if (button_check(&button_l) == 1) { oled_print("L"); }
    if (button_check(&button_r) == 1) { oled_print("R"); }
  }
}
