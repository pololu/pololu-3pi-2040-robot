// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#pragma once

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

void led_yellow(bool);

void rgb_start_frame(void);
void rgb_end_frame(size_t count);
void rgb_write(uint8_t red, uint8_t green, uint8_t blue, uint8_t brightness);
void rgb_clear(void);
void rgb_init(void);
