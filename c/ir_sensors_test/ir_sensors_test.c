// This shows how to read the IR sensors (5 line sensors and 2 bump sensors)
// on the Pololu 3pi+ 2040 Robot.

#include <stdio.h>
#include <string.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

bool calibrate = 0;
bool use_calibrated_read = 0;

void draw_options()
{
  if (calibrate)
  {
    display_text("cal line sensor\u2026", 0, 0, COLOR_WHITE_ON_BLACK);
    display_text("A: stop         ", 0, 8, COLOR_WHITE_ON_BLACK);
  }
  else
  {
    display_text("A: calibrate    ", 0, 0, COLOR_WHITE_ON_BLACK);
    display_text("C: switch mode  ", 0, 8, COLOR_WHITE_ON_BLACK);
  }
}

// Draws a bar at the bottom of the screen, 8 pixels wide and up to 32 pixels
// tall.
// value should be between 0 and 1024.
void draw_bar(uint32_t x, uint32_t value, uint32_t cal_min, uint32_t cal_max)
{
  // Draw the main bar, indicating the value.
  // Number of pixels = value / 4.
  int height = value / 32;
  uint8_t remainder = value / 4 & 7;
  for (uint8_t page = 7; page >= 4; page--)
  {
    for (uint32_t i = 0; i < 8; i++)
    {
      uint8_t mask = 0;
      int local_height = height + (i < remainder);
      if (local_height >= 0) { mask = -256 >> local_height; }

      display_buffer[page * DISPLAY_WIDTH + x + i] = mask;
    }
    height -= 8;
  }

  // Draw the notches indicating the calibration range.
  // Prevent a left shift by a negative amount below.
  if (cal_min >= 1024) { cal_min = 1023; }
  if (cal_max >= 1024) { cal_max = 1023; }
  uint32_t cal_mask = 0;
  if (cal_max)
  {
    cal_mask = 1 << (31 - cal_min / 32) | 1 << (31 - cal_max / 32);
  }
  for (uint8_t page = 4; page < 8; page++)
  {
    display_buffer[page * DISPLAY_WIDTH + x + 8] = cal_mask;
    display_buffer[page * DISPLAY_WIDTH + x + 9] = cal_mask;
    cal_mask >>= 8;
  }
}

int main()
{
  stdio_init_all();
  display_init();
  draw_options();
  display_show();

  while (1)
  {
    bump_sensors_read();
    line_sensors_read_calibrated();

    if (calibrate) { line_sensors_calibrate(); }

    // TODO: use button presses instead of just USB commands
    int cmd = getchar_timeout_us(0);
    if (cmd == 'a')
    {
      printf("got a\n");
      if (calibrate == 0)
      {
        // TODO: bump_sensors_calibrate();
        //display_text("calibrated bump    ", 0, 0, COLOR_WHITE_ON_BLACK);
        //display_text("sensors            ", 0, 8, COLOR_WHITE_ON_BLACK);
        //display_show();
        //sleep_ms(500);

        calibrate = 1;
      }
      else
      {
        calibrate = 0;
      }
      draw_options();
    }
    if (cmd == 'c')
    {
      use_calibrated_read = !use_calibrated_read;
    }
    if (cmd == 'd')
    {
      // Dump everything to the serial port.
      printf("raw:       %4u %4u %4u %4u %4u %4u %4u\n",
        bump_sensor_left,
        line_sensors[0],
        line_sensors[1],
        line_sensors[2],
        line_sensors[3],
        line_sensors[4],
        bump_sensor_right);
      printf("cal_min:   %4u %4u %4u %4u %4u %4u %4u\n",
        1024 /*TODO*/,
        line_sensors_cal_min[0],
        line_sensors_cal_min[1],
        line_sensors_cal_min[2],
        line_sensors_cal_min[3],
        line_sensors_cal_min[4],
        1024 /*TODO*/);
      printf("cal_max:   %4u %4u %4u %4u %4u %4u %4u\n",
        0 /*TODO*/,
        line_sensors_cal_max[0],
        line_sensors_cal_max[1],
        line_sensors_cal_max[2],
        line_sensors_cal_max[3],
        line_sensors_cal_max[4],
        0 /*TODO*/);
    }
    if (cmd == 'r')
    {
      line_sensors_reset_calibration();
    }

    if (use_calibrated_read)
    {
      // TODO: show calibrated bump sensor readings
      for (unsigned int i = 0; i < 5; i++)
      {
        draw_bar(24 + i * 16, line_sensors_calibrated[i], 1024, 0);
      }
    }
    else
    {
      draw_bar(0, bump_sensor_left, 1024, 0);
      for (unsigned int i = 0; i < 5; i++)
      {
        draw_bar(24 + i * 16, line_sensors[i], line_sensors_cal_min[i], line_sensors_cal_max[i]);
      }
      draw_bar(112, bump_sensor_right, 1024, 0);
    }

    display_show();
  }
}
