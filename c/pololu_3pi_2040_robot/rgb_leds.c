// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pico/stdlib.h>
#include <hardware/spi.h>
#include <pololu_3pi_2040_robot.h>

#define RGB_DATA_PIN 3
#define RGB_CLOCK_PIN 6

static void rgb_leds_start_frame()
{
  // This is a faster version of:
  //   spi_set_baudrate(spi0, 20000000);
  //   spi_set_format(spi0, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_LSB_FIRST);
  // Frequency = 125 MHz / CPSR / (SCR + 1) = 125 MHz / 2 / (3 + 1) = 15.6 MHz
  spi0_hw->cpsr = 2;
  spi0_hw->cr0 = 0x307;  // SCR = 3. DSS = 0b111: 8-bit data.

  gpio_set_function(RGB_CLOCK_PIN, GPIO_FUNC_SPI);
  gpio_set_function(RGB_DATA_PIN, GPIO_FUNC_SPI);

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

  gpio_set_function(RGB_DATA_PIN, GPIO_FUNC_NULL);  // stop driving
  gpio_set_function(RGB_CLOCK_PIN, GPIO_FUNC_SIO);  // drive low
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
  spi_init(spi0, 20000000);

  gpio_init(RGB_CLOCK_PIN);
  gpio_set_dir(RGB_CLOCK_PIN, GPIO_OUT);

  rgb_leds_off();
}
