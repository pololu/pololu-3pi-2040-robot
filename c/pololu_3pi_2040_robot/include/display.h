// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file display.h
/// This header provides functions that make it easy to show Unicode text and
/// graphics on the OLED display.

#pragma once

// A font where each character is 8 pixels wide and 16 pixels tall.
// Refer to the comments in font_8x16.c to see which Unicode characters are
// included and how to write them in a C string.
extern const uint8_t font_8x16[];

// A font where each character is 8 pixels wide and 8 pixels tall.
// Refer to the comments in font_8x8.c to see which Unicode characters are
// included and how to write them in a C string.
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
#define COLOR_BLACK 0

/// In a drawing operation, this specifies changing foreground pixels to
/// 1 (which is normally white) and leaving background pixels unchanged.
#define COLOR_WHITE 1

/// In a drawing operation, this specifies changing foreground pixels to
/// 0 and changing background pixels to 1.
#define COLOR_BLACK_ON_WHITE 2

/// In a drawing operation, this specifies changing foreground pixels to
/// 1 and changing background pixels to 0.
#define COLOR_WHITE_ON_BLACK 3

/// In a drawing operation, this specifies inverting the color of foreground
/// pixels and leaving background pixels unchanged.
#define COLOR_XOR 4

/// A flag that can be passed to certain display functions indicating that they
/// should show their changes to the OLED before returning.
#define DISPLAY_NOW 0x800

/// Calls sh1106_init() to initialize the OLED and also clears the graphics
/// buffer.
///
/// You should generally call this before calling any other display functions.
void display_init(void);

/// Sets the font to be used in text drawing operations.
///
/// @param A pointer to one of the fonts declared in this header, or a font
/// data structure with a compatible format.
void display_set_font(const uint32_t * font);

/// Fills the entire graphics buffer with zeroes or ones.
/// @param color 0 or 1
void display_fill(uint8_t color);

/// Sets the color of a specific pixel.
///
/// It is OK to pass coordinates that are outside the bounds of the screen.
///
/// @param x The column of the pixel (0 = left side).
/// @param y The row of the pixel (0 = top side).
/// @param flags The lower byte of this argument should be 1 or 0 to indicate
///   what color to set the pixel to, or COLOR_XOR to toggle the color.
///   If you want to immediately write the specified pixel to the OLED display,
///   use bitwise OR (|) to combine this color with DISPLAY_NOW.
void display_pixel(uint32_t x, uint32_t y, uint32_t flags);

/// Gets the color of a specific pixel.
///
/// @param x The column of the pixel (0 = left side).
/// @param y The row of the pixel (0 = top side).
/// @return 0 or 1
bool display_get_pixel(uint32_t x, uint32_t y);

/// @brief Writes text to the frame buffer and optionally to the display.
///
/// You can specify which font to use by calling display_set_font().
///
/// For good performance, the text must be aligned:
/// - y must be a multiple of 8.
/// - x must be a multiple of 4.
///
/// Writing unaligned text can increase the run time of this function by about
/// 40 to 80 microseconds per character.
///
/// @param string A null-terminated, UTF-8 encoded string.
/// @param x The left-most column of the text (0 = left side of screen).
/// @param y The top-most row of the text (0 = top side of screen).
/// @param flags
///   The lower byte of this argument should be 1 for white text,
///   0 for black text, or one of the other COLOR_* macros to indicate how
///   to draw the text.
///   If you want to immediately write the text to the OLED display, use
///   bitwise OR (|) to combine this color with DISPLAY_NOW.
/// @return A number between 0 and 128 that is one plus the x coordinate of the
///   rightmost column the on-screen portion of the text.
///   (If none of the text is on the screen, the return value is unspecified.)
///   This can be used to measure text.
uint32_t display_text(const char * string, int32_t x, int32_t y, uint32_t flags);

/// Writes the specified rectangular region of the graphics buffer to the
/// display.
///
/// It is OK to pass coordinates that are outside the bounds of the screen.
///
/// @param x_left The left-most column of the rectangle.
/// @param x_right The right-most column of the rectangle.
/// @param y_top The top-most row of the rectangle.
/// @param y_bottom The bottom-most row of the rectangle.
void display_show_partial(uint32_t x_left, uint32_t x_right,
  uint32_t y_top, uint32_t y_bottom);

/// Writes the entire graphics buffer to the display.
void display_show(void);
