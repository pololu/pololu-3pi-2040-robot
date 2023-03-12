// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pololu_3pi_2040_robot.h>
#include <string.h>
#include <assert.h>

uint8_t display_buffer[1024];

// TODO: we want to get these values from the font so we can allow fonts of
// different sizes (at least 8x16, 8x8, 5x8, 10x16).
#define FONT_WIDTH 8
#define FONT_HEIGHT 16

static const uint32_t * find_glyph(const uint32_t * font, uint32_t codepoint)
{
  uint32_t glyph_count = font[1];
  uint32_t mask = font[2];
  uint32_t longs_per_glyph = font[3];
  uint32_t i = 0;
  while (true)
  {
    if ((i | mask) < glyph_count)
    {
      uint32_t codepoint_found = font[6 + (i | mask)];
      if (codepoint_found == codepoint)
      {
        return &font[6 + glyph_count + longs_per_glyph * (i | mask)];
      }
      if (codepoint_found < codepoint)
      {
        i |= mask;
      }
    }
    if (mask == 0)
    {
      // Character not found
      if (codepoint == 0x25A1)
      {
        // White square not found, just return the first glyph.
        return &font[6 + glyph_count];
      }
      else
      {
        // Find the white square instead.
        return find_glyph(font, 0x25A1);
      }
    }
    mask >>= 1;
  }
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

uint32_t display_text_aligned(const char * text, uint32_t x, uint32_t y, uint32_t flags)
{
  assert((y & 7) == 0);
  if (x + 8 > 128 || y + 16 > 64) { return 0; }

  size_t left_x = x;

  while (1)
  {
    uint32_t c = *text++;
    if (c == 0 || x + 8 > 128) { break; }
    if (0x80 & c)
    {
      // Convert UTF-8 bytes to a codepoint.
      uint8_t n = *text++;
      if (n == 0) { break; }
      c = (c & 0x3F) << 6 | (n & 0x3F);
      if (0x20 << 6 & c)
      {
        n = *text++;
        if (n == 0) { break; }
        c = (c & 0x7FF) << 6 | (n & 0x3F);
      }
      if (0x10 << 12 & c)
      {
        n = *text++;
        if (n == 0) { break; }
        c = (c & 0x7FFF) << 6 | (n & 0x3F);
      }
    }

    const uint32_t * glyph = find_glyph(oled_font, c);

    uint8_t * b = &display_buffer[y * 16 + x];
    for (size_t i = 0; i < FONT_LONGS_PER_GLYPH; i++)
    {
      uint32_t g = glyph[i];
      b[i * 2] = g & 0xFF;
      b[i * 2 + 128] = g >> 8 & 0xFF;
      b[i * 2 + 1] = g >> 16 & 0xFF;
      b[i * 2 + 128 + 1] = g >> 24 & 0xFF;
    }
    x += 8;
  }

  if (flags & DISPLAY_NOW)
  {
    display_show_rectangle(left_x, x, y, y + FONT_HEIGHT);
  }

  return x;
}

uint32_t display_text(const char * text, uint32_t x, uint32_t y, uint32_t flags)
{
  if (x >= 128 || y >= 64) { return 0; }

  if ((y & 7) == 0)
  {
    return display_text_aligned(text, x, y, flags);
  }

  // TODO: implement slow path
  return 0;
}

void display_show_rectangle(uint32_t x_left, uint32_t x_right, uint32_t y_top, uint32_t y_bottom)
{
  assert(x_left <= x_right);
  assert(x_right <= 128);
  assert(y_top <= y_bottom);
  assert(y_bottom <= 64);

  sh1106_transfer_start();
  for (unsigned int page = y_top >> 3; page < y_bottom >> 3; page++)
  {
    sh1106_write(page, x_left, display_buffer + page * 128 + x_left, x_right - x_left);
  }
  sh1106_transfer_end();
}

void display_show()
{
  sh1106_transfer_start();
  for (unsigned int page = 0; page < 8; page++)
  {
    sh1106_write_page(page, display_buffer + page * 128);
  }
  sh1106_transfer_end();
}
