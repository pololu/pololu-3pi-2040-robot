// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pico/stdlib.h>
#include <hardware/spi.h>
#include <pololu_3pi_plus_2040_robot.h>

// TODO: these names should start with "rgb_leds_"

void rgb_start_frame(void)
{
  gpio_set_function(6, GPIO_FUNC_SPI);
  gpio_set_function(3, GPIO_FUNC_SPI);

  uint8_t start_frame[] = { 0, 0, 0, 0 };
  spi_write_blocking(spi0, start_frame, sizeof(start_frame));
}

void rgb_end_frame(size_t count)
{
  uint8_t zero = 0;
  for (size_t i = 0; i < (count + 14)/16; i++)
  {
    spi_write_blocking(spi0, &zero, 1);
  }

  gpio_set_function(6, GPIO_FUNC_SIO);
  gpio_deinit(3);
}

void rgb_write(uint8_t red, uint8_t green, uint8_t blue, uint8_t brightness)
{
  uint8_t frame[] = { 0xE0 | (brightness & 0x1F), blue, green, red };
  spi_write_blocking(spi0, frame, sizeof(frame));
}

void rgb_clear(void)
{
  rgb_start_frame();
  for (size_t i = 0; i < 6; i++) { rgb_write(0, 0, 0, 0); }
  rgb_end_frame(6);
}

void rgb_init(void)
{
  // Note: We'd have to rethink how we are initializing things here if we
  // want the OLED to also use hardware SPI.

  // Drive the clock line low.
  gpio_init(6);
  gpio_set_dir(6, GPIO_OUT);

  spi_init(spi0, 400000);
  spi_set_format(spi0, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_LSB_FIRST);

  rgb_clear();
}
