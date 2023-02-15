// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

// Low-level library for the SH1106 OLED display.

// TODO: Use hardware SPI instead of GPIO

#include <pico/stdlib.h>
#include <pololu_3pi_plus_2040_robot.h>

#define SH1106_DC_PIN 0
#define SH1106_RES_PIN 1
#define SH1106_CLK_PIN 2
#define SH1106_MOS_PIN 3

void sh1106_init_pins(void)
{
  gpio_init(SH1106_RES_PIN);
  gpio_set_dir(SH1106_RES_PIN, GPIO_OUT);

  gpio_init(SH1106_CLK_PIN);
  gpio_set_dir(SH1106_CLK_PIN, GPIO_OUT);
}

void sh1106_reset(void)
{
  gpio_put(SH1106_RES_PIN, 0);
  sleep_us(10);
  gpio_put(SH1106_RES_PIN, 1);
  sleep_us(10);
}

void sh1106_transfer_start(void)
{
  gpio_init(SH1106_MOS_PIN);
  gpio_set_dir(SH1106_MOS_PIN, GPIO_OUT);

  gpio_init(SH1106_DC_PIN);
  gpio_set_dir(SH1106_DC_PIN, GPIO_OUT);
}

void sh1106_transfer_end(void)
{
  gpio_deinit(SH1106_MOS_PIN);
  gpio_deinit(SH1106_DC_PIN);
}

void sh1106_command_mode(void)
{
  gpio_put(SH1106_DC_PIN, 0);
}

void sh1106_data_mode(void)
{
  gpio_put(SH1106_DC_PIN, 1);
}

// Experimentally, we found that there needs to be one NOP between "str"
// instructions writing to OLED pins or else the communication is too fast.
// Let's use 4 to be a little extra safe.
static void sh1106_delay(void)
{
  __asm__("nop\n" "nop\n" "nop\n" "nop\n");
}

// Note: We should try rewriting this to use hardware SPI.
void sh1106_write(uint8_t d)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    gpio_put(SH1106_CLK_PIN, 0);
    sh1106_delay();
    gpio_put(SH1106_MOS_PIN, d & 0x80);
    sh1106_delay();
    gpio_put(SH1106_CLK_PIN, 1);
    sh1106_delay();
    d <<= 1;
  }
}

void sh1106_start_page_write(uint8_t page)
{
  sh1106_command_mode();
  sh1106_write(SH1106_SET_PAGE_ADDR | page);
  sh1106_write(SH1106_SET_COLUMN_ADDR_HIGH | 0);
  sh1106_write(SH1106_SET_COLUMN_ADDR_LOW | 2);
  sh1106_data_mode();
}

void sh1106_clear(void)
{
  sh1106_transfer_start();
  sh1106_command_mode();
  sh1106_write(SH1106_SET_COLUMN_ADDR_LOW | 2);
  for (uint8_t page = 0; page < 8; page++)
  {
    sh1106_start_page_write(page);
    for (uint8_t i = 0; i < 128; i++)
    {
      sh1106_write(0);
    }
  }
  sh1106_transfer_end();
}

void sh1106_configure_default(void)
{
  sh1106_transfer_start();
  sh1106_command_mode();
  sh1106_write(SH1106_SET_SEGMENT_REMAP | 1);  // flip horizontally
  sh1106_write(SH1106_SET_COM_SCAN_DIR | 8);   // flip vertically
  sh1106_write(SH1106_SET_CONTRAST);
  sh1106_write(0xFF);                // maximum brightness
  sh1106_write(SH1106_SET_DISPLAY_ON | 1);
  sh1106_transfer_end();
}

void sh1106_init(void)
{
  sh1106_init_pins();

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
