// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file sh1106.h
/// This header provides low-level functions for writing to the OLED.
/// For a higher-level API with documentation, see display.h.

#pragma once

#include <stdint.h>
#include <stdbool.h>

#define SH1106_SET_COLUMN_ADDR_LOW 0x00
#define SH1106_SET_COLUMN_ADDR_HIGH 0x10
#define SH1106_SET_CONTRAST 0x81
#define SH1106_SET_SEGMENT_REMAP 0xA0
#define SH1106_SET_INVERT_DISPLAY 0xA6
#define SH1106_SET_DISPLAY_ON 0xAE
#define SH1106_SET_PAGE_ADDR 0xB0
#define SH1106_SET_COM_SCAN_DIR 0xC0

void sh1106_reset(void);
void sh1106_transfer_start(void);
void sh1106_transfer_end(void);
void sh1106_command_mode(void);
void sh1106_data_mode(void);
void sh1106_write_page(uint8_t page, uint8_t x, const uint8_t * data, uint32_t length);
void sh1106_clear(void);
void sh1106_configure_default(void);
void sh1106_sleep(bool sleep);
void sh1106_contrast(uint8_t contrast);
void sh1106_invert(bool invert);
void sh1106_rotate(uint16_t angle);  // 0 or 180
void sh1106_init(void);
