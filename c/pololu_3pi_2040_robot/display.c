// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

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
  size_t glyph_count = font->glyph_count;
  size_t mask = font->mask;
  uint8_t glyph_size = font->glyph_size;
  const uint8_t * data = font->data;
  size_t i = 0;
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

void display_pixel(unsigned int x, unsigned int y, uint8_t flags)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return; }
  uint8_t * p = display_buffer + (y >> 3) * DISPLAY_WIDTH + x;
  color8_funcs[flags & COLOR_MASK_NO_BG](p, 1 << (y & 7));
  if (flags & DISPLAY_NOW) { display_show_partial(x, y, 1, 1); }
}

bool display_get_pixel(unsigned int x, unsigned int y)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return 0; }
  return display_buffer[(y >> 3) * DISPLAY_WIDTH + x] >> (y & 7) & 1;
}

// Faster version of display_text.
//
// It does 32-bit writes (8x4 pixels), so x must be 4-aligned
// and y must be 8-aligned.
static int display_text_aligned(const char * text, int x, int y,
  uint8_t flags)
{
  int left_x = x;
  uint8_t font_width = display_font->font_width;
  uint8_t font_height = display_font->font_height;

  color32_func color = color32_funcs[flags & COLOR_MASK];

  // Address of the upper left sliver of the next display_buffer location.
  // Use uintptr_t instead of a pointer type because this could point to invalid
  // locations before or after display_buffer.
  uintptr_t b = ((uintptr_t)&display_buffer) + (unsigned int)y * 16 + x;

  while (1)
  {
    uint32_t c = *text++;
    if (c & 0x80) { c = read_utf8_continuation(&text, c); }
    if (c == 0) { break; }

    const uint32_t * glyph = (const uint32_t *)find_glyph(display_font, c);

    if ((unsigned int)y < DISPLAY_HEIGHT)
    {
      if ((unsigned int)x < DISPLAY_WIDTH)
      {
        color((void *)b, glyph[0]);                         // Upper left 8x4
      }
      if ((unsigned int)(x + 4) < DISPLAY_WIDTH)
      {
        color((void *)(b + 4), glyph[1]);                   // Upper right 8x4
      }
    }

    if (font_height > 8 && (unsigned int)(y + 8) < DISPLAY_HEIGHT)
    {
      if ((unsigned int)x < DISPLAY_WIDTH)
      {
        color((void *)(b + DISPLAY_WIDTH), glyph[2]);       // Lower left 8x4
      }
      if ((unsigned int)(x + 4) < DISPLAY_WIDTH)
      {
        color((void *)(b + DISPLAY_WIDTH + 4), glyph[3]);   // Lower right 8x4
      }
    }

    b += font_width;
    x = (unsigned int)x + font_width;  // avoid C undefined behavior
  }

  if (flags & DISPLAY_NOW)
  {
    display_show_partial(left_x, y, (unsigned int)x - left_x, font_height);
  }

  return x;
}

// Assumption: the font width is 8, and gx and gy are valid coordinates.
static bool glyph_get_pixel(const uint8_t * glyph, unsigned int gx, unsigned int gy)
{
  return glyph[(gy & ~7) + gx] >> (gy & 7) & 1;
}

int display_text(const char * text, int x, int y, uint8_t flags)
{
  if ((x & 3) == 0 && (y & 7) == 0)
  {
    return display_text_aligned(text, x, y, flags);
  }

  int left_x = x;
  uint8_t font_width = display_font->font_width;
  uint8_t font_height = display_font->font_height;

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

    for (uint8_t gx = 0; gx < font_width; gx++)
    {
      for (uint8_t gy = 0; gy < font_height; gy++)
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
    x = (unsigned int)x + font_width;  // avoid C undefined behavior
  }

  if (flags & DISPLAY_NOW)
  {
    display_show_partial(left_x, y, (unsigned int)x - left_x, font_height);
  }

  return x;
}

void display_fill_rect(int x, int y, int width, int height, uint8_t flags)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return; }
  if (width <= 0 || height <= 0) { return; }  // Avoid underflows below
  if (x < 0) { width += x; x = 0; }
  if (y < 0) { height += y; y = 0; }
  if (width <= 0 || height <= 0) { return; }
  if (width > DISPLAY_WIDTH - x) { width = DISPLAY_WIDTH - x; }
  if (height > DISPLAY_HEIGHT - y) { height = DISPLAY_HEIGHT - y; }

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
    display_show_partial(x, y, width, height);
  }
}

void display_show_partial(int x, int y, int width, int height)
{
  if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) { return; }
  if (width <= 0 || height <= 0) { return; }  // Avoid underflows below
  if (x < 0) { width += x; x = 0; }
  if (y < 0) { height += y; y = 0; }
  if (width <= 0 || height <= 0) { return; }
  if (width > DISPLAY_WIDTH - x) { width = DISPLAY_WIDTH - x; }
  if (height > DISPLAY_HEIGHT - y) { height = DISPLAY_HEIGHT - y; }

  sh1106_transfer_start();
  unsigned int last_page = (y + height - 1) >> 3;
  for (unsigned int page = y >> 3; page <= last_page; page++)
  {
    sh1106_write_page(page, x,
      display_buffer + page * DISPLAY_WIDTH + x, width);
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
