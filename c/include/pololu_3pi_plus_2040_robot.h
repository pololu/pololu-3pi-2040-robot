// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

// TODO: demo or function for detecting USB power

#pragma once

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

void yellow_led(bool);

uint16_t battery_get_level_millivolts(void);

bool button_a_is_pressed(void);
bool button_b_is_pressed(void);
bool button_c_is_pressed(void);

typedef struct rgb_color {
  uint8_t red, green, blue;
} rgb_color;

// brightness should be between 1 and 31.
void rgb_leds_write(rgb_color * colors, size_t count, uint8_t brightness);
void rgb_leds_off(void);
void rgb_leds_init(void);

#define SH1106_SET_COLUMN_ADDR_LOW 0x00
#define SH1106_SET_COLUMN_ADDR_HIGH 0x10
#define SH1106_SET_CONTRAST 0x81
#define SH1106_SET_SEGMENT_REMAP 0xA0
#define SH1106_SET_INVERT_DISPLAY 0xA6
#define SH1106_SET_DISPLAY_ON 0xAE
#define SH1106_SET_PAGE_ADDR 0xB0
#define SH1106_SET_COM_SCAN_DIR 0xC0

void sh1106_init_pins(void);
void sh1106_reset(void);
void sh1106_transfer_start(void);
void sh1106_transfer_end(void);
void sh1106_command_mode(void);
void sh1106_data_mode(void);
void sh1106_write(uint8_t);
void sh1106_start_page_write(uint8_t page);
void sh1106_clear(void);
void sh1106_configure_default(void);
void sh1106_init(void);

extern uint16_t bump_sensor_left, bump_sensor_right, line_sensors[5];
void ir_sensors_read_bump(void);
void ir_sensors_read_line(void);
