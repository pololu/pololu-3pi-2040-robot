// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

// Low-level library for the SH1106 OLED display.

#include <sh1106.h>
#include <pico/stdlib.h>
#include <hardware/spi.h>

#define SH1106_DC_PIN 0
#define SH1106_RES_PIN 1
#define SH1106_CLK_PIN 2
#define SH1106_MOS_PIN 3

static uint16_t sh1106_cpsr;
static uint16_t sh1106_cr0;

void sh1106_reset()
{
  gpio_put(SH1106_RES_PIN, 0);
  sleep_us(10);
  gpio_put(SH1106_RES_PIN, 1);
  sleep_us(10);
}

void sh1106_transfer_start()
{
  // Quickly restore the correct clock frequency and format options.
  spi0_hw->cpsr = sh1106_cpsr;
  spi0_hw->cr0 = sh1106_cr0;

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

void sh1106_write_page(uint8_t page, uint8_t x, const uint8_t * data, uint32_t length)
{
  sh1106_command_mode();
  uint8_t column = x + 2;
  uint8_t cmd[] = {
    SH1106_SET_PAGE_ADDR | page,
    SH1106_SET_COLUMN_ADDR_HIGH | (column >> 4),
    SH1106_SET_COLUMN_ADDR_LOW | (column & 0xF),
  };
  spi_write_blocking(spi0, cmd, sizeof(cmd));
  sh1106_data_mode();
  spi_write_blocking(spi0, data, length);
}

void sh1106_clear()
{
  uint8_t empty[128] = { 0 };
  sh1106_transfer_start();
  sh1106_command_mode();
  for (uint8_t page = 0; page < 8; page++)
  {
    sh1106_write_page(page, 0, empty, 128);
  }
  sh1106_transfer_end();
}

static void sh1106_cmd(const uint8_t * cmd, uint32_t size)
{
  sh1106_transfer_start();
  sh1106_command_mode();
  spi_write_blocking(spi0, cmd, size);
  sh1106_transfer_end();
}

void sh1106_configure_default()
{
  uint8_t cmd[] = {
    SH1106_SET_SEGMENT_REMAP | 1,  // flip horizontally
    SH1106_SET_COM_SCAN_DIR | 8,   // flip vertically
    SH1106_SET_CONTRAST, 0xFF,     // maximum brightness
    SH1106_SET_INVERT_DISPLAY,     // no invert
    SH1106_SET_DISPLAY_ON | 1,
  };
  sh1106_cmd(cmd, sizeof(cmd));
}

void sh1106_sleep(bool sleep)
{
  uint8_t cmd[] = { SH1106_SET_DISPLAY_ON | !sleep };
  sh1106_cmd(cmd, sizeof(cmd));
}

void sh1106_contrast(uint8_t contrast)
{
  uint8_t cmd[] = { SH1106_SET_CONTRAST, contrast };
  sh1106_cmd(cmd, sizeof(cmd));
}

void sh1106_invert(bool invert)
{
  uint8_t cmd[] = { SH1106_SET_INVERT_DISPLAY | invert };
  sh1106_cmd(cmd, sizeof(cmd));
}

void sh1106_rotate(uint16_t angle)
{
  if (angle == 0 || angle == 180)
  {
    bool flip = angle == 0;
    uint8_t cmd[] = {
      SH1106_SET_SEGMENT_REMAP | flip,      // flip horizontally
      SH1106_SET_COM_SCAN_DIR | flip << 3,  // flip vertically
    };
    sh1106_cmd(cmd, sizeof(cmd));
  }
}

void sh1106_init()
{
  // The SH1106 datasheet specifies a maximum SPI frequency of 4 MHz, but it
  // seems to work fine up to at least 31 MHz.
  spi_init(spi0, 20000000);
  sh1106_cpsr = spi0_hw->cpsr;
  sh1106_cr0 = spi0_hw->cr0;

  gpio_init(SH1106_RES_PIN);
  gpio_set_dir(SH1106_RES_PIN, GPIO_OUT);

  gpio_init(SH1106_CLK_PIN);
  gpio_set_dir(SH1106_CLK_PIN, GPIO_OUT);

  // Give the OLED some time to start up.  Without this, it sometimes gets
  // misconfigured and displays things in the wrong positions, espcially
  // when plugging USB into a robot that has been unpowered for a while.
  absolute_time_t oled_ready;
  update_us_since_boot(&oled_ready, 20000);
  sleep_until(oled_ready);

  sh1106_reset();
  sh1106_clear();
  sh1106_configure_default();
}
