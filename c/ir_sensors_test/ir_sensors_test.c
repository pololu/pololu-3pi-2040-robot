// TODO

#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_plus_2040_robot.h>

void show_bar(uint8_t page, uint8_t width)
{
  sh1106_start_page_write(page);
  for (uint8_t x = 0; x < 128; x++)
  {
    sh1106_write(x < width ? 0xFE : 0x00);
  }
}


int main()
{
  stdio_init_all();
  sh1106_init();

  while (1)
  {
    ir_sensors_read_line();
    ir_sensors_read_bump();

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
