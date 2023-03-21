// This shows how to read the IR sensors (5 line sensors and 2 bump sensors)
// on the Pololu 3p+ 2040 Robot.  The readings are displayed on the OLED and
// printed to the USB virtual serial port.

#include <stdio.h>
#include <string.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

void show_bar(uint8_t page, uint8_t width)
{
  uint8_t data[128] = { 0 };
  memset(data, 0xFE, width);
  sh1106_write_page(page, 0, data, 128);
}

int main()
{
  stdio_init_all();
  sh1106_init();

  while (1)
  {
    line_sensors_read();
    bump_sensors_read();

    sh1106_transfer_start();
    for (uint8_t i = 0; i < 5; i++)
    {
      uint8_t width = line_sensors[i] * 128 / 1024;
      show_bar(i, width);
    }
    show_bar(6, bump_sensor_left * 128 / 1024);
    show_bar(7, bump_sensor_right * 128 / 1024);
    sh1106_transfer_end();

    printf("%4u %4u %4u %4u %4u %4u %4u\n",
      bump_sensor_left,
      bump_sensor_right,
      line_sensors[0],
      line_sensors[1],
      line_sensors[2],
      line_sensors[3],
      line_sensors[4]);

    yellow_led(time_us_32() >> 18 & 1);
  }
}
