// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

// Low-level library for the SH1106 OLED display.

#include <pico/stdlib.h>
#include <hardware/spi.h>
#include <pololu_3pi_2040_robot.h>

#define SH1106_DC_PIN 0
#define SH1106_RES_PIN 1
#define SH1106_CLK_PIN 2
#define SH1106_MOS_PIN 3

void sh1106_reset(void)
{
  gpio_put(SH1106_RES_PIN, 0);
  sleep_us(10);
  gpio_put(SH1106_RES_PIN, 1);
  sleep_us(10);
}

void sh1106_transfer_start(void)
{
  // This is a faster version of:
  //   spi_set_baudrate(spi0, 10000000);
  //   spi_set_format(spi0, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_LSB_FIRST);
  // Frequency = 125 MHz / CPSR / (SCR + 1) = 125 MHz / 2 / (6 + 1) = 8.9 MHz
  spi0_hw->cpsr = 2;
  spi0_hw->cr0 = 0x607;  // SCR = 6. DSS = 0b111: 8-bit data.

  gpio_set_function(SH1106_CLK_PIN, GPIO_FUNC_SPI);
  gpio_set_function(SH1106_MOS_PIN, GPIO_FUNC_SPI);
  gpio_set_function(SH1106_DC_PIN, GPIO_FUNC_SIO);
  gpio_set_dir(SH1106_DC_PIN, GPIO_OUT);
}

void sh1106_transfer_end()
{
  gpio_set_function(SH1106_DC_PIN, GPIO_FUNC_NULL);   // stop driving
  gpio_set_function(SH1106_MOS_PIN, GPIO_FUNC_NULL);  // stop driving
  gpio_set_function(SH1106_CLK_PIN, GPIO_FUNC_SIO);   // drive low
}

void sh1106_command_mode()
{
  gpio_put(SH1106_DC_PIN, 0);
}

void sh1106_data_mode()
{
  gpio_put(SH1106_DC_PIN, 1);
}

void sh1106_start_page_write(uint8_t page)
{
  sh1106_command_mode();
  uint8_t cmd[] = {
    SH1106_SET_PAGE_ADDR | page,
    SH1106_SET_COLUMN_ADDR_HIGH | 0,
    SH1106_SET_COLUMN_ADDR_LOW | 2,
  };
  spi_write_blocking(spi0, cmd, sizeof(cmd));
  sh1106_data_mode();
}

void sh1106_page_write(uint8_t page, uint8_t * data)
{
  sh1106_start_page_write(page);
  spi_write_blocking(spi0, data, 128);
}

void sh1106_clear()
{
  uint8_t empty[128] = { 0 };
  sh1106_transfer_start();
  sh1106_command_mode();
  for (uint8_t page = 0; page < 8; page++)
  {
    sh1106_page_write(page, empty);
  }
  sh1106_transfer_end();
}

void sh1106_configure_default()
{
  sh1106_transfer_start();
  sh1106_command_mode();
  uint8_t cmd[] = {
    SH1106_SET_SEGMENT_REMAP | 1,  // flip horizontally
    SH1106_SET_COM_SCAN_DIR | 8,   // flip vertically
    SH1106_SET_CONTRAST, 0xFF,     // maximum brightness
    SH1106_SET_DISPLAY_ON | 1,
  };
  spi_write_blocking(spi0, cmd, sizeof(cmd));
  sh1106_transfer_end();
}

void sh1106_init()
{
  spi_init(spi0, 10000000);

  gpio_init(SH1106_RES_PIN);
  gpio_set_dir(SH1106_RES_PIN, GPIO_OUT);

  gpio_init(SH1106_CLK_PIN);
  gpio_set_dir(SH1106_CLK_PIN, GPIO_OUT);

  // Sometimes the OLED doesn't get initialized properly and stays off,
  // or displays its pages in the incorrect positions,
  // especially when plugging USB into an unpowered 3pi04a board.
  // This delay seems to fix that, but I haven't characterized the necessary
  // timing carefully.
  absolute_time_t oled_ready;
  update_us_since_boot(&oled_ready, 20000);
  sleep_until(oled_ready);

  sh1106_reset();
  sh1106_clear();
  sh1106_configure_default();
}
