// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pololu_3pi_2040_robot.h>
#include <string.h>
#include <assert.h>

uint8_t display_buffer[1024];

#define FONT_HEADER_SIZE 6  // in units of 4 bytes
#define WHITE_SQUARE_UTF8 0xE296A1  // "\u25A1"

static const uint32_t * find_glyph(const uint32_t * font, uint32_t code)
{
  uint32_t glyph_count = font[1];
  uint32_t mask = font[2];
  uint32_t glyph_size = font[3];  // in units of 4 bytes
  uint32_t i = 0;
  while (true)
  {
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
    if (mask == 0)
    {
      // Character not found.
      if (code == WHITE_SQUARE_UTF8)
      {
        // White square not found, so just return the first glyph.
        return &font[FONT_HEADER_SIZE + glyph_count];
      }
      else
      {
        return find_glyph(font, WHITE_SQUARE_UTF8);
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
  x &= ~3;  // We do 32-bit writes (8x4 pixels), so x should be 4-aligned.
  y &= ~7;  // SH1106 pages are 8 pixels tall, so y should be 8-aligned.

  size_t left_x = x;
  uint32_t font_width = oled_font[4];
  uint32_t font_height = oled_font[5];
  uint32_t max_x = 128 - font_width;

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

    const uint32_t * glyph = find_glyph(oled_font, c);

    uint32_t * b = (uint32_t *)&display_buffer[y * 16 + x];
    b[0] = glyph[0];
    b[1] = glyph[1];
    if (font_height > 8)
    {
      b[32] = glyph[2];
      b[33] = glyph[3];
    }

    x += font_width;
  }

  if (flags & DISPLAY_NOW)
  {
    display_show_partial(left_x, x, y, y + font_height);
  }

  return x;
}

uint32_t display_text(const char * text, uint32_t x, uint32_t y, uint32_t flags)
{
  if (x >= 128 || y >= 64) { return 0; }

  if ((x & 3) == 0 && (y & 7) == 0)
  {
    return display_text_aligned(text, x, y, flags);
  }

  // TODO: implement slow path
  return 0;
}

void display_show_partial(uint32_t x_left, uint32_t x_right, uint32_t y_top, uint32_t y_bottom)
{
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
