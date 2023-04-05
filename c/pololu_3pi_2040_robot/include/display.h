// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file display.h
/// This header provides functions that make it easy to show Unicode text and
/// graphics on the OLED display.

#pragma once

#include <stdbool.h>
#include <stdint.h>

/// A font where each character is 8 pixels wide and 16 pixels tall,
/// defined in font_8x16.c.
extern const uint8_t font_8x16[];

/// A font where each character is 8 pixels wide and 8 pixels tall,
/// defined in font_8x8.c.
extern const uint8_t font_8x8[];

/// The width of the display, in pixels.
#define DISPLAY_WIDTH 128

/// The height of the display, in pixels.
#define DISPLAY_HEIGHT 64

/// A graphics buffer that holds one frame to be shown on the OLED.
///
/// Each byte of the graphics buffer represents a 1x8 vertical column of pixels,
/// with the least-significant bit holding the top-most pixel.
/// The first byte represents the pixels in the upper left corner of the screen,
/// and the bytes in the buffer are ordered left-to-right, then top-to-bottom.
/// (So byte at offset 128 is displayed immediately below the byte at offset 0.)
extern uint8_t display_buffer[1024];

/// In a drawing operation, this specifies changing foreground pixels to
/// 0 (which is normally black) and leaving background pixels unchanged.
///
/// For compatibility with the MicroPython framebuf class, this macro should
/// always have a value of 0.
#define COLOR_BLACK 0

/// In a drawing operation, this specifies changing foreground pixels to
/// 1 (which is normally white) and leaving background pixels unchanged.
///
/// For compatibility with the MicroPython framebuf class, this macro should
/// always have a value of 1.
#define COLOR_WHITE 1

/// In a drawing operation, this specifies inverting the color of foreground
/// pixels and leaving background pixels unchanged.
#define COLOR_XOR 2

/// In a drawing operation, this specifies not changing any pixels.
#define COLOR_NOP 3

/// In a drawing operation, this specifies changing foreground pixels to
/// 0 and changing background pixels to 1.
#define COLOR_BLACK_ON_WHITE 4

/// In a drawing operation, this specifies changing foreground pixels to
/// 1 and changing background pixels to 0.
#define COLOR_WHITE_ON_BLACK 5

/// A flag that can be passed to certain display functions indicating that they
/// should show their changes to the OLED before returning.
#define DISPLAY_NOW 0x80

/// Calls sh1106_init() to initialize the OLED and also clears the graphics
/// buffer.
///
/// You should generally call this before calling any other display functions.
void display_init(void);

/// Sets the font to be used in text drawing operations.
///
/// @param font A pointer to one of the fonts declared in this header.
void display_set_font(const uint8_t * font);

/// Fills the entire graphics buffer with zeroes or ones.
/// @param color 0 or 1
void display_fill(uint8_t color);

/// Sets the color of a specific pixel.
///
/// It is OK to pass coordinates that are outside the bounds of the screen.
///
/// @param x The column of the pixel (0 = left side).
/// @param y The row of the pixel (0 = top side).
/// @param flags The lower 2 bits of this argument should be 1 or 0 to indicate
///   what color to set the pixel to, or COLOR_XOR or COLOR_NOP.
///   If you want to immediately write the specified pixel to the OLED display,
///   use bitwise OR (|) to combine this color with DISPLAY_NOW.
void display_pixel(unsigned int x, unsigned int y, uint8_t flags);

/// Gets the color of a specific pixel.
///
/// @param x The column of the pixel (0 = left side).
/// @param y The row of the pixel (0 = top side).
/// @return 0 or 1
bool display_get_pixel(unsigned int x, unsigned int y);

/// @brief Writes text to the frame buffer and optionally to the display.
///
/// The default font is font_8x8 (8 pixels wide, 8 pixels tall).
/// You can specify which font to use by calling display_set_font().
///
/// For good performance, the text should be aligned:
/// - y should be a multiple of 8.
/// - x should be a multiple of 4.
///
/// @param string A null-terminated, UTF-8 encoded string.
/// @param x The left-most column of the text (0 = left side of screen).
/// @param y The top-most row of the text (0 = top side of screen).
/// @param flags
///   The lower 3 bits of this argument should be one of the COLOR_* macros.
///   If you want to immediately write the text to the OLED display, use
///   bitwise OR (|) to combine this color with DISPLAY_NOW.
/// @return Returns one plus the x coordinate of the rightmost column of the
///   text.
int display_text(const char * string, int x, int y, uint8_t flags);

/// @brief Draws a solid rectangle.
/// @param x The left-most column of the rectangle (0 = left side of screen).
/// @param y The top-most row of the rectangle (0 = top side of screen).
/// @param width The width of the rectangle.
/// @param height The height of the rectangle.
/// @param flags
//    The lower 2 bits of this argument should be 1 or 0 to indicate
///   what color to fill the rectangle with, or COLOR_XOR or COLOR_NOP.
///   If you want to immediately write the text to the OLED display, use
///   bitwise OR (|) to combine this color with DISPLAY_NOW.
void display_fill_rect(int x, int y, int width, int height, uint8_t flags);

/// Writes the specified rectangular region of the graphics buffer to the
/// display.
///
/// It is OK to pass coordinates that are partially or fully outside the bounds
/// of the screen.
///
/// @param x The left-most column of the rectangle (0 = left side of screen).
/// @param y The top-most row of the rectangle (0 = top side of screen).
/// @param width The width of the rectangle.
/// @param height The height of the rectangle.
void display_show_partial(int x, int y, int width, int height);

/// Writes the entire graphics buffer to the display.
void display_show(void);
