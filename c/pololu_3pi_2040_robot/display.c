// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pololu_3pi_2040_robot.h>
#include <string.h>

uint8_t display_buffer[1024];

static const uint32_t * find_glyph(const uint32_t * font, uint32_t codepoint)
{
  uint32_t glyph_count = font[0];

  uint32_t i = 0;
  uint32_t mask = 0x80;
  while (mask <= glyph_count >> 1){ mask <<= 1; }
  while (true)
  {
    if ((i | mask) < glyph_count)
    {
      const uint32_t * entry = font + 5 + (i | mask) * 5;
      uint32_t codepoint_found = entry[0];
      if (codepoint_found == codepoint)
      {
        return entry + 1;
      }
      if (codepoint_found < codepoint)
      {
        i |= mask;
      }
    }
    if (mask == 0)
    {
      return font + 1;  // Character not found
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

void display_text_aligned(const char * text, size_t x, size_t y, uint8_t color)
{
  (void)color; // TODO: implement color argument
  assert((y & 7) == 0);
  if (x + 8 > 128 || y + 16 > 64) { return; }

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
    for (size_t i = 0; i < 4; i++)
    {
      uint32_t g = glyph[i];
      b[i * 2] = g & 0xFF;
      b[i * 2 + 128] = g >> 8 & 0xFF;
      b[i * 2 + 1] = g >> 16 & 0xFF;
      b[i * 2 + 128 + 1] = g >> 24 & 0xFF;
    }
    x += 8;
  }
}

// TODO: implement color argument
void display_text(const char * text, size_t x, size_t y, uint8_t color)
{
  if (x >= 128 || y >= 64) { return; }

  if ((y & 7) == 0)
  {
    display_text_aligned(text, x, y, color);
  }

  // TODO: implement slow path
}

void display_show()
{
  sh1106_transfer_start();
  for (unsigned int page = 0; page < 8; page++)
  {
    sh1106_page_write(page, display_buffer + page * 128);
  }
  sh1106_transfer_end();
}