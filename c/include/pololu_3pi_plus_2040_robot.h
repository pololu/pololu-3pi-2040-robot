// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#pragma once

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

void yellow_led(bool);

bool button_a_is_pressed(void);
bool button_b_is_pressed(void);
bool button_c_is_pressed(void);

void rgb_leds_start_frame(void);
void rgb_leds_end_frame(size_t count);
void rgb_leds_write(uint8_t red, uint8_t green, uint8_t blue, uint8_t brightness);
void rgb_leds_off(void);
void rgb_leds_init(void);

