// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pico/stdlib.h>
#include <hardware/spi.h>
#include <pololu_3pi_2040_robot.h>

static void rgb_leds_start_frame()
{
  gpio_set_function(6, GPIO_FUNC_SPI);
  gpio_set_function(3, GPIO_FUNC_SPI);

  uint8_t start_frame[] = { 0, 0, 0, 0 };
  spi_write_blocking(spi0, start_frame, sizeof(start_frame));
}

static void rgb_leds_end_frame(size_t count)
{
  uint8_t zero = 0;
  for (size_t i = 0; i < (count + 14)/16; i++)
  {
    spi_write_blocking(spi0, &zero, 1);
  }

  gpio_set_function(6, GPIO_FUNC_SIO);
  gpio_deinit(3);
}

void rgb_leds_write(rgb_color * colors, size_t count, uint8_t brightness)
{
  rgb_leds_start_frame();
  uint8_t frame[4] = { 0xE0 | (brightness & 0x1F) };
  for (size_t i = 0; i < count; i++)
  {
    frame[1] = colors[i].blue;
    frame[2] = colors[i].green;
    frame[3] = colors[i].red;
    spi_write_blocking(spi0, frame, sizeof(frame));
  }
  rgb_leds_end_frame(count);
}

void rgb_leds_off()
{
  rgb_color blank[6] = { 0 };
  rgb_leds_write(blank, 6, 0);
}

void rgb_leds_init()
{
  // Note: We'd have to rethink how we are initializing things here if we
  // want the OLED to also use hardware SPI.

  spi_init(spi0, 20000000);
  spi_set_format(spi0, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_LSB_FIRST);

  rgb_leds_off();
}
