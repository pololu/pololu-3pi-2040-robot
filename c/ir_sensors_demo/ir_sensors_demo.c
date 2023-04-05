// Demonstrates the IR sensors on the 3pi+ robot: the left and right
// bump sensors on the front of the robot and the five downward-looking
// reflectance/line sensors.
//
// Press button A to calibrate both sets of sensors.
//
// Press button C to switch the line sensors to display calibrated or
// uncalibrated values.
//
// On the USB virtual serial port, you can type "a" or "c" to perform the
// same same functions as the corresponding buttons.
// Type "d" to dump relevant sensor data and calibration values.
// Type "r" to reset the calibration.

#include <stdio.h>
#include <string.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

button button_a = BUTTON_INIT(button_a_is_pressed);
button button_b = BUTTON_INIT(button_b_is_pressed);
button button_c = BUTTON_INIT(button_c_is_pressed);

bool calibrate = 0;
bool use_calibrated_read = 0;

void draw_options()
{
  if (calibrate)
  {
    // Uses Unicode 0x2026 (…) instead of "..." to save two characters.
    display_text("cal line sensor…", 0, 0, COLOR_WHITE_ON_BLACK);
    display_text("A: stop         ", 0, 8, COLOR_WHITE_ON_BLACK);
  }
  else
  {
    display_text("A: calibrate    ", 0, 0, COLOR_WHITE_ON_BLACK);
    display_text("C: switch mode  ", 0, 8, COLOR_WHITE_ON_BLACK);
  }
}

void draw_mode()
{
  if (use_calibrated_read)
  {
    display_text("Calibrated", 0, 16, COLOR_WHITE_ON_BLACK);
  }
  else
  {
    display_text("Raw       ", 0, 16, COLOR_WHITE_ON_BLACK);
  }
}

void draw_notch(uint32_t x, uint32_t value)
{
  uint32_t y = DISPLAY_HEIGHT - 1 - value / 32;
  if (y < 32) { y = 32; }
  if (y >= DISPLAY_HEIGHT) { y = DISPLAY_HEIGHT - 1; }
  display_fill_rect(x, y, 2, 1, 1);
}

// Draws a bar at the bottom of the screen to indicate an IR sensor reading
// between 0 and 1024.
// The number of illuminated pixels in the bar will be value/4, meaning
// each pixel represents 4 counts.
// Also draws small notches indicating the calibration range.
void draw_bar(uint32_t x, uint32_t value, uint32_t cal_min, uint32_t cal_max)
{
  if (value > 1024) { value = 1024; }

  uint32_t pixels = value / 4;

  // Draw the main bar.
  uint32_t height = pixels / 8;
  display_fill_rect(x, DISPLAY_HEIGHT - height, 8, height, 1);

  // Draw extra pixels on top of the bar to provide 3 more bits of resolution.
  uint8_t remainder = pixels % 8;
  display_fill_rect(x, DISPLAY_HEIGHT - 1 - height, remainder, 1, 1);

  // Draw the notches indicating the calibration values.
  if (cal_min <= 1024)
  {
    draw_notch(x + 8, cal_min);
  }
  if (cal_max > 0 && cal_max <= 1024)
  {
    draw_notch(x + 8, cal_max);
  }
}

// This non-blocking function returns a character representing a press event
// for a button on the robot, or a character received from the virtual serial
// port, or -1 if there is no input from either source.
char check_input()
{
  if (button_check(&button_a) == 1) { return 'a'; }
  if (button_check(&button_b) == 1) { return 'b'; }
  if (button_check(&button_c) == 1) { return 'c'; }
  return getchar_timeout_us(0);
}

int main()
{
  stdio_init_all();
  display_init();
  draw_options();
  draw_mode();

  while (1)
  {
    bump_sensors_read();
    line_sensors_read_calibrated();

    if (calibrate) { line_sensors_calibrate(); }

    int cmd = check_input();
    if (cmd == 'a')
    {
      calibrate = !calibrate;
      if (calibrate)
      {
        bump_sensors_calibrate();
        display_fill(0);
        display_text("calibrated bump", 0, 0, COLOR_WHITE_ON_BLACK);
        display_text("sensors", 0, 8, COLOR_WHITE_ON_BLACK);
        display_show();
        sleep_ms(500);
      }
      draw_options();
      draw_mode();
    }
    if (cmd == 'c')
    {
      use_calibrated_read = !use_calibrated_read;
      draw_mode();
    }
    if (cmd == 'd')
    {
      // Dump everything to the virtual serial port.
      printf("raw:        %4u %4u %4u %4u %4u %4u %4u\n",
        bump_sensors[0],
        line_sensors[0],
        line_sensors[1],
        line_sensors[2],
        line_sensors[3],
        line_sensors[4],
        bump_sensors[1]);
      printf("cal_min:    %4u %4u %4u %4u %4u %4u %4u\n",
        bump_sensors_threshold_min[0],
        line_sensors_cal_min[0],
        line_sensors_cal_min[1],
        line_sensors_cal_min[2],
        line_sensors_cal_min[3],
        line_sensors_cal_min[4],
        bump_sensors_threshold_min[1]);
      printf("cal_max:    %4u %4u %4u %4u %4u %4u %4u\n",
        bump_sensors_threshold_max[0],
        line_sensors_cal_max[0],
        line_sensors_cal_max[1],
        line_sensors_cal_max[2],
        line_sensors_cal_max[3],
        line_sensors_cal_max[4],
        bump_sensors_threshold_max[1]);
      printf("calibrated: %4u %4u %4u %4u %4u %4u %4u\n\n",
        bump_sensors_pressed[0],
        line_sensors_calibrated[0],
        line_sensors_calibrated[1],
        line_sensors_calibrated[2],
        line_sensors_calibrated[3],
        line_sensors_calibrated[4],
        bump_sensors_pressed[1]);
    }
    if (cmd == 'r')
    {
      line_sensors_reset_calibration();
      bump_sensors_reset_calibration();
    }

    // Redraw the bottom half of the display.
    display_fill_rect(0, 32, 128, 32, 0);
    if (use_calibrated_read)
    {
      draw_bar(0, bump_sensors_pressed[0] * 1024, 1025, 1025);
      for (unsigned int i = 0; i < 5; i++)
      {
        draw_bar(24 + i * 16, line_sensors_calibrated[i], 1025, 1025);
      }
      draw_bar(112, bump_sensors_pressed[1] * 1024, 1025, 1025);
    }
    else
    {
      // Scale the bump sensor readings up so they are easier to see
      const uint8_t bump_scale = 2;
      draw_bar(0, bump_sensors[0] * bump_scale,
        bump_sensors_threshold_min[0] * bump_scale,
        bump_sensors_threshold_max[0] * bump_scale);
      for (unsigned int i = 0; i < 5; i++)
      {
        draw_bar(24 + i * 16, line_sensors[i],
          line_sensors_cal_min[i], line_sensors_cal_max[i]);
      }
      draw_bar(112, bump_sensors[1] * bump_scale,
        bump_sensors_threshold_min[1] * bump_scale,
        bump_sensors_threshold_max[1] * bump_scale);
    }

    display_show();
  }
}
