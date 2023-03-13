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

void sh1106_reset(void);
void sh1106_transfer_start(void);
void sh1106_transfer_end(void);
void sh1106_command_mode(void);
void sh1106_data_mode(void);
void sh1106_write(uint8_t page, uint8_t x, const uint8_t * data, uint32_t length);
void sh1106_write_page(uint8_t page, uint8_t * data);
void sh1106_clear(void);
void sh1106_configure_default(void);
void sh1106_init(void);

extern const unsigned long oled_font[];

extern uint8_t display_buffer[1024];
#define DISPLAY_NOW 0x800
// TODO: add flags to specify the color
void display_init(void);
void display_fill(uint8_t color);
uint32_t display_text_aligned(const char * string, uint32_t x, uint32_t y, uint32_t flags);
uint32_t display_text(const char * string, uint32_t x, uint32_t y, uint32_t flags);
void display_show_rectangle(uint32_t x_left, uint32_t x_right, uint32_t y_top, uint32_t y_bottom);
void display_show(void);

extern uint16_t bump_sensor_left, bump_sensor_right, line_sensors[5];
void ir_sensors_read_bump(void);
void ir_sensors_read_line(void);

#define MOTORS_MAX_SPEED 6000
void motors_init(void);
void motors_flip_left(bool flip);
void motors_flip_right(bool flip);
void motors_set_left_speed(int32_t speed);
void motors_set_right_speed(int32_t speed);
void motors_set_speeds(int32_t left_speed, int32_t right_speed);
