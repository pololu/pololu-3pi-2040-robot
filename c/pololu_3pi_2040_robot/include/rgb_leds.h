// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file rgb_leds.h
///
/// Functions for writing to the APA102-compatible RGB LEDs on the
/// control board.

#pragma once

#include <stdint.h>

/// Represents a color that can be written to the RGB LEDs.
typedef struct rgb_color {
  /// The value of the red component, from 0 to 255.
  uint8_t red;

  /// The value of the green component, from 0 to 255.
  uint8_t green;

  /// The value of the blue component, from 0 to 255.
  uint8_t blue;
} rgb_color;

/// Writes the specified array of colors to the RGB LEDs.
///
/// @param colors An array of colors to write to the LEDs.
///   The first one is written to LED A, and the second one is written to
///   to LED B, and so on.
/// @param count The number of colors in the array.
/// @param brightness The global brightness, from 0 to 31.
void rgb_leds_write(rgb_color * colors, uint32_t count, uint8_t brightness);

/// Turns off the first six RGB LEDs by setting them to black.
void rgb_leds_off(void);

/// Initializes the RGB LED routines.
///
/// This should be called before calling any other functions in this file.
void rgb_leds_init(void);
