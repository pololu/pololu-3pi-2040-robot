// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pololu_3pi_2040_robot.h>
#include <string.h>
#include <assert.h>

#define FONT_HEADER_SIZE 6  // in units of 4 bytes
#define WHITE_SQUARE_UTF8 0xE296A1  // "\u25A1"

const uint32_t checkerboard[] = { 0xCCCC3333, 0xCCCC3333, 0xCCCC3333, 0xCCCC3333 };

const uint32_t * display_font = font_8x8;

uint8_t display_buffer[1024];

void display_set_font(const uint32_t * font)
{
  display_font = font;
}

static const uint32_t * find_glyph(const uint32_t * font, uint32_t code)
{
  uint32_t glyph_count = font[1];
  uint32_t mask = font[2];
  uint32_t glyph_size = font[3];  // in units of 4 bytes
  uint32_t i = 0;
  while (mask)
  {
    mask >>= 1;
    if ((i | mask) < glyph_count)
    {
      uint32_t code_found = font[FONT_HEADER_SIZE + (i | mask)];
      if (code_found == code)
      {
        return &font[FONT_HEADER_SIZE + glyph_count + glyph_size * (i | mask)];
      }
      if (code_found < code)
      {
        i |= mask;
      }
    }
  }
  if (code != WHITE_SQUARE_UTF8)
  {
    // Character not found, so try to find the white square.
    return find_glyph(font, WHITE_SQUARE_UTF8);
  }
  // White square not found, so just return a checkerboard.
  return checkerboard;
}

void display_init()
{
  sh1106_init();
  memset(display_buffer, 0, sizeof(display_buffer));
}

void display_fill(uint8_t color)
{
  if (color == 1)
  {
    memset(display_buffer, 0xFF, sizeof(display_buffer));
  }
  else if (color == 0)
  {
    memset(display_buffer, 0, sizeof(display_buffer));
  }
}

void color_0(uint32_t * dest, uint32_t src) { *dest &= ~src; }
void color_1(uint32_t * dest, uint32_t src) { *dest |= src; }
void color_0_on_1(uint32_t * dest, uint32_t src) { *dest = ~src; }
void color_1_on_0(uint32_t * dest, uint32_t src) { *dest = src; }
void color_xor(uint32_t * dest, uint32_t src) { *dest = src; }

typedef void (* color_func)(uint32_t *, uint32_t);
color_func color_funcs[] = {
  // The first two colors are the same as MicroPython's framebuf.text().
  color_0,
  color_1,
  color_0_on_1,
  color_1_on_0,
  color_xor,
  color_1,  // reserved
  color_1,  // reserved
  color_1,  // reserved
};
#define COLOR_MASK 7

void display_pixel(uint32_t x, uint32_t y, uint32_t flags)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return; }
  uint8_t page = y >> 3;
  uint8_t mask = 1 << (y & 7);
  uint8_t * p = &display_buffer[page * DISPLAY_WIDTH + x];
  uint32_t sliver = *p;
  color_funcs[flags & COLOR_MASK](&sliver, mask);
  *p = (*p & ~mask) | (sliver & mask);
  if (flags & DISPLAY_NOW) { display_show_partial(x, x, y, y); }
}

bool display_get_pixel(uint32_t x, uint32_t y)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return 0; }
  return display_buffer[(y >> 3) * DISPLAY_WIDTH + x] >> (y & 7) & 1;
}

// We do 32-bit writes (8x4 pixels), so x should be 4-aligned.
// SH1106 pages are 8 pixels tall, so y should be 8-aligned.
static uint32_t display_text_aligned(const char * text, uint32_t x, uint32_t y,
  uint32_t flags)
{
  size_t left_x = x;
  uint32_t font_width = display_font[4];
  uint32_t font_height = display_font[5];
  uint32_t max_x = DISPLAY_WIDTH - font_width;

  color_func color = color_funcs[flags & COLOR_MASK];

  if (y + font_height > 64) { return 0; }

  while (x <= max_x)
  {
    // Collect the UTF-8 continuation bytes for this character, but break
    // if we reach the end of the string.
    uint32_t c = *text++;
    if (c == 0) { break; }
    if (0x80 & c)
    {
      uint8_t n = *text++;
      if (n == 0) { break; }
      c = c << 8 | n;
      if (0x2000 & c)
      {
        n = *text++;
        if (n == 0) { break; }
        c = c << 8 | n;
        if (0x100000 & c)
        {
          n = *text++;
          if (n == 0) { break; }
          c = c << 8 | n;
        }
      }
    }

    const uint32_t * glyph = find_glyph(display_font, c);

    uint32_t * b = (uint32_t *)&display_buffer[y * 16 + x];
    color(&b[0], glyph[0]);
    color(&b[1], glyph[1]);
    if (font_height > 8)
    {
      color(&b[32], glyph[2]);
      color(&b[33], glyph[3]);
    }

    x += font_width;
  }

  if (flags & DISPLAY_NOW)
  {
    display_show_partial(left_x, x - 1, y, y + font_height - 1);
  }

  return x;
}

uint32_t display_text(const char * text, uint32_t x, uint32_t y, uint32_t flags)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return 0; }

  if ((x & 3) == 0 && (y & 7) == 0)
  {
    return display_text_aligned(text, x, y, flags);
  }

  // TODO: implement slow path so people can do unaligned text
  return 0;
}

void display_show_partial(uint32_t x_left, uint32_t x_right,
  uint32_t y_top, uint32_t y_bottom)
{
  if (x_left >= DISPLAY_WIDTH || y_top >= DISPLAY_HEIGHT) { return; }
  if (x_left > x_right || y_top > y_bottom) { return; }
  sh1106_transfer_start();
  for (unsigned int page = y_top >> 3; page <= y_bottom >> 3; page++)
  {
    sh1106_write(page, x_left, display_buffer + page * DISPLAY_WIDTH + x_left,
      x_right + 1 - x_left);
  }
  sh1106_transfer_end();
}

void display_show()
{
  sh1106_transfer_start();
  for (unsigned int page = 0; page < 8; page++)
  {
    sh1106_write_page(page, display_buffer + page * DISPLAY_WIDTH);
  }
  sh1106_transfer_end();
}
