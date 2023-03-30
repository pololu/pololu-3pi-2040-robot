// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

// TODO: change display_text to take 'int' arguments for
// easier porting back to AVRs and consistency with display_fill_rect.
// TODO: use 'unsigned int' and 'int' wherever it makes sense, for easier porting
// to AVRs.
// TODO: make 'flags' be a uint8_t everywhere for the same reason?
// TODO: change display_show_partial args to be the same as the first four of
// display_fill_rect, or at least justify the difference

#include <display.h>
#include <string.h>
#include <assert.h>
#include <sh1106.h>

static inline unsigned int to_unsigned(int x) { return x < 0 ? 0 : x; }

typedef struct font_header {
  uint32_t size;
  uint32_t glyph_count;
  uint32_t mask;
  uint8_t glyph_size;
  uint8_t font_width;
  uint8_t font_height;
  uint8_t _padding;
  uint8_t data[];
} font_header;

#define WHITE_SQUARE 0x25A1

const uint8_t checkerboard[] = {
  0x33, 0x33, 0xCC, 0xCC,
  0x33, 0x33, 0xCC, 0xCC,
  0x33, 0x33, 0xCC, 0xCC,
  0x33, 0x33, 0xCC, 0xCC,
};

const font_header * display_font = (void *)font_8x8;

uint8_t display_buffer[1024];

void display_set_font(const uint8_t * font)
{
  display_font = (void *)font;
}

static const uint8_t * find_glyph(const font_header * font, uint32_t code)
{
  uint32_t glyph_count = font->glyph_count;
  uint32_t mask = font->mask;
  uint32_t glyph_size = font->glyph_size;
  const uint8_t * data = font->data;
  uint32_t i = 0;
  while (mask)
  {
    mask >>= 1;
    if ((i | mask) < glyph_count)
    {
      uint32_t code_found = ((uint32_t *)data)[i | mask];
      if (code_found == code)
      {
        return data + 4 * glyph_count + glyph_size * (i | mask);
      }
      if (code_found < code)
      {
        i |= mask;
      }
    }
  }
  if (code != WHITE_SQUARE)
  {
    // Character not found, so try to find the white square.
    return find_glyph(font, WHITE_SQUARE);
  }
  // White square not found, so just return a checkerboard.
  return checkerboard;
}

// Given the first byte of a multi-byte UTF8 character sequence and a
// pointer to a pointer to the bytes following it, this function reads the
// remaining bytes for the UTF8 character and returns the code point.
// Returns 0 if the end of the string is found (indicating invalid encoding).
// Does not check for other possible misencodings.
static uint32_t read_utf8_continuation(const char ** text, uint32_t c)
{
  uint8_t n = *(*text)++;
  if (n == 0) { return 0; }
  c = (c & 0x3F) << 6 | (n & 0x3F);        // c bits: 0 0000 0000 xxxx xxyy yyyy
  if (c & 0x800)
  {
    n = *(*text)++;
    if (n == 0) { return 0; }
    c = (c & 0x7FF) << 6 | (n & 0x3F);     // c bits: 0 000x xxxx yyyy yyzz zzzz
    if (c & 0x10000)
    {
      n = *(*text)++;
      if (n == 0) { return 0; }
      c = (c & 0x7FFF) << 6 | (n & 0x3F);  // c bits: x xxyy yyyy zzzz zzqq qqqq
    }
  }
  return c;
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

#define COLOR_MASK_NO_BG 3
#define COLOR_MASK 7

void color32_0(uint32_t * dest, uint32_t src) { *dest &= ~src; }
void color32_1(uint32_t * dest, uint32_t src) { *dest |= src; }
void color32_0_on_1(uint32_t * dest, uint32_t src) { *dest = ~src; }
void color32_1_on_0(uint32_t * dest, uint32_t src) { *dest = src; }
void color32_xor(uint32_t * dest, uint32_t src) { *dest ^= src; }
void color32_nop(uint32_t * dest, uint32_t src) { (void)dest; (void)src; }

typedef void (* color32_func)(uint32_t *, uint32_t);
color32_func color32_funcs[] = {
  // The first two colors are the same as MicroPython's framebuf.text().
  color32_0,
  color32_1,
  color32_xor,
  color32_nop,
  color32_0_on_1,
  color32_1_on_0,
  color32_nop,  // reserved
  color32_nop,  // reserved
};

void color8_0(uint8_t * dest, uint8_t src) { *dest &= ~src; }
void color8_1(uint8_t * dest, uint8_t src) { *dest |= src; }
void color8_0_on_1(uint8_t * dest, uint8_t src) { *dest = ~src; }
void color8_1_on_0(uint8_t * dest, uint8_t src) { *dest = src; }
void color8_xor(uint8_t * dest, uint8_t src) { *dest ^= src; }
void color8_nop(uint8_t * dest, uint8_t src) { (void)dest; (void)src; }

typedef void (* color8_func)(uint8_t *, uint8_t);
color8_func color8_funcs[] = {
  // The first two colors are the same as MicroPython's framebuf.text().
  color8_0,
  color8_1,
  color8_xor,
  color8_nop,
  color8_0_on_1,
  color8_1_on_0,
  color8_nop,  // reserved
  color8_nop,  // reserved
};

void display_pixel(uint32_t x, uint32_t y, uint32_t flags)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return; }
  uint8_t page = y >> 3;
  uint8_t * p = display_buffer + page * DISPLAY_WIDTH + x;
  color8_funcs[flags & COLOR_MASK_NO_BG](p, 1 << (y & 7));
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
  uint32_t font_width = display_font->font_width;
  uint32_t font_height = display_font->font_height;
  uint32_t max_x = DISPLAY_WIDTH - font_width;

  color32_func color = color32_funcs[flags & COLOR_MASK];

  if (y + font_height > 64) { return 0; }

  while (x <= max_x)
  {
    uint32_t c = *text++;
    if (c & 0x80) { c = read_utf8_continuation(&text, c); }
    if (c == 0) { break; }

    const uint32_t * glyph = (const uint32_t *)find_glyph(display_font, c);

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

// Assumption: the font width is 8, and gx and gy are valid coordinates.
static bool glyph_get_pixel(const uint8_t * glyph, uint32_t gx, uint32_t gy)
{
  return glyph[(gy & ~7) + gx] >> (gy & 7) & 1;
}

// TODO: fix the behavior when x < 0 but still aligned, I think no text will get displayed
// TODO: fix the behavior when y is -8, I think there will be out of bounds writes in display_text_aligned
// TODO: make sure we can draw 8x16 text where only the top or bottom half is visible,
// preferably with draw_text_aligned but maybe that's asking too much
uint32_t display_text(const char * text, int32_t x, int32_t y, uint32_t flags)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return 0; }

  if ((x & 3) == 0 && (y & 7) == 0)
  {
    return display_text_aligned(text, x, y, flags);
  }

  size_t left_x = x;
  uint32_t font_width = display_font->font_width;
  uint32_t font_height = display_font->font_height;

  uint8_t fg = flags & COLOR_MASK, bg = COLOR_NOP;
  switch (fg)
  {
  case COLOR_BLACK_ON_WHITE: fg = COLOR_BLACK; bg = COLOR_WHITE; break;
  case COLOR_WHITE_ON_BLACK: fg = COLOR_WHITE; bg = COLOR_BLACK; break;
  }

  while (1)
  {
    uint32_t c = *text++;
    if (c & 0x80) { c = read_utf8_continuation(&text, c); }
    if (c == 0) { break; }

    const uint8_t * glyph = find_glyph(display_font, c);

    for (uint32_t gx = 0; gx < font_width; gx++)
    {
      for (uint32_t gy = 0; gy < font_height; gy++)
      {
        if (glyph_get_pixel(glyph, gx, gy))
        {
          display_pixel(x + gx, y + gy, fg);
        }
        else if (bg != COLOR_NOP)
        {
          display_pixel(x + gx, y + gy, bg);
        }
      }
    }
    x += font_width;
  }

  if (flags & DISPLAY_NOW)
  {
    display_show_partial(left_x, x - 1, y, y + font_height - 1);
  }

  if (x > DISPLAY_WIDTH) { x = DISPLAY_WIDTH; }
  return x;
}

void display_fill_rect(int x, int y, int width, int height, uint32_t flags)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return; }
  if (width <= 0 || height <= 0) { return; }  // Avoid underflows below
  if (x < 0) { width += x; x = 0; }
  if (y < 0) { height += y; y = 0; }
  if (width <= 0 || height <= 0) { return; }

  color8_func color = color8_funcs[flags & COLOR_MASK_NO_BG];

  unsigned int last_page = (y + height - 1) >> 3;
  for (unsigned int page = y >> 3; page <= last_page; page++)
  {
    uint8_t * p = display_buffer + page * DISPLAY_WIDTH + x;
    int rel_y = y - page * 8;
    uint8_t mask = 0xFFu << to_unsigned(rel_y) & 0xFFu >> to_unsigned(8 - rel_y - height);
    for (int i = 0; i < width; i++) { color(p + i, mask); }
  }

  if (flags & DISPLAY_NOW)
  {
    display_show_partial(x, x + width - 1, y, y + height - 1);
  }
}

void display_show_partial(uint32_t x_left, uint32_t x_right,
  uint32_t y_top, uint32_t y_bottom)
{
  if (x_left >= DISPLAY_WIDTH || y_top >= DISPLAY_HEIGHT) { return; }
  if (x_left > x_right || y_top > y_bottom) { return; }
  if (x_right >= DISPLAY_WIDTH) { x_right = DISPLAY_WIDTH - 1; }
  if (y_bottom >= DISPLAY_HEIGHT) { y_bottom = DISPLAY_HEIGHT - 1; }
  sh1106_transfer_start();
  for (unsigned int page = y_top >> 3; page <= y_bottom >> 3; page++)
  {
    sh1106_write_page(page, x_left,
      display_buffer + page * DISPLAY_WIDTH + x_left, x_right + 1 - x_left);
  }
  sh1106_transfer_end();
}

void display_show()
{
  sh1106_transfer_start();
  for (unsigned int page = 0; page < 8; page++)
  {
    sh1106_write_page(page, 0,
      display_buffer + page * DISPLAY_WIDTH, DISPLAY_WIDTH);
  }
  sh1106_transfer_end();
}
