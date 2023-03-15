#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

void show_bar(uint8_t page, uint8_t width)
{
  uint8_t data[128];
  for (uint8_t x = 0; x < 128; x++)
  {
    data[x] = x < width ? 0xFE : 0x00;
  }
  sh1106_write_page(page, data);
}

void report(uint32_t time, const char * name)
{
  size_t name_length = printf("%s: ", name);
  for (size_t i = name_length; i < 40; i++) { putchar(' '); }
  printf("%ld\n", time);

  sleep_ms(500);
  while (button_a_is_pressed());
}

int main()
{
  stdio_init_all();
  display_init();

  uint32_t start, end;

  while (1)
  {
    putchar('\n');

    start = time_us_32();
    display_fill(0);
    display_show();
    report(time_us_32() - start, "Clear");

    start = time_us_32();
    for (uint8_t i = 0; i < 128; i++)
    {
      display_pixel(i, (i * 13) % 128, DISPLAY_NOW | 1);
    }
    report(time_us_32() - start, "64 pixels");

    //// 8x16 text /////////////////////////////////////////////////////////////
    display_set_font(font_8x16);
    display_fill(0);
    display_show();

    start = time_us_32();
    display_text("hi:)", 0, 0, DISPLAY_NOW | 1);
    report(time_us_32() - start, "8x16: 4-char ASCII update");

    start = time_us_32();
    display_text("hello world :):)", 0, 0, DISPLAY_NOW | COLOR_BLACK_ON_WHITE);
    report(time_us_32() - start, "8x16: 16-char ASCII update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→☺𝟅", 0, 16, DISPLAY_NOW | 1);
    report(time_us_32() - start, "8x16: 16-char Unicode update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→☺𝟅", 0, 16, COLOR_BLACK_ON_WHITE);
    end = time_us_32();
    display_show();
    report(end - start, "8x16: 16-char Unicode render");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→☺𝟅", 0, 36, COLOR_BLACK_ON_WHITE);
    end = time_us_32();
    display_show();
    report(end - start, "8x16: 16-char Unicode render unaligned");

    start = time_us_32();
    display_fill(0);
    display_text("Full update!    ", 0, 0, 1);
    display_text("Tall 8x16 font  ", 0, 16, 1);
    display_text("& some unicode  ", 0, 32, 1);
    display_text("°±²µΔΘΩθμπ…←↑→☺𝟅", 0, 48, 1);
    display_show();
    report(time_us_32() - start, "8x16: full update");

    //// 8x8 text /////////////////////////////////////////////////////////////
    display_set_font(font_8x8);
    display_fill(0);
    display_show();

    start = time_us_32();
    display_text("hi:)", 0, 0, DISPLAY_NOW | 1);
    report(time_us_32() - start, "8x8: 4-char ASCII update");

    start = time_us_32();
    display_text("hello world :):)", 0, 0, DISPLAY_NOW | COLOR_BLACK_ON_WHITE);
    report(time_us_32() - start, "8x8: 16-char ASCII update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→☺𝟅", 0, 8, DISPLAY_NOW | 1);
    report(time_us_32() - start, "8x8: 16-char Unicode update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→☺𝟅", 0, 8, COLOR_BLACK_ON_WHITE);
    end = time_us_32();
    display_show();
    report(end - start, "8x8: 16-char Unicode draw");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→☺𝟅", 0, 20, COLOR_BLACK_ON_WHITE);
    end = time_us_32();
    display_show();
    report(end - start, "8x8: 16-char Unicode draw unaligned");

    start = time_us_32();
    display_fill(0);
    display_text("Full update!    ", 0, 0, COLOR_XOR);
    display_text("Short 8x8 font  ", 0, 8, 1);
    display_text("& some unicode  ", 0, 16, 1);
    display_text("°±²µΔΘΩθμπ…←↑→☺𝟅", 0, 24, COLOR_BLACK_ON_WHITE);
    display_text("Important for   ", 0, 32, 1);
    display_text("people who want ", 0, 40, 1);
    display_text("lots of data!   ", 0, 48, 1);
    display_text("☺☻♡♥☺☻♡♥☺☻♡♥☺☻♡♥", 0, 56, 1);
    display_show();
    report(time_us_32() - start, "8x8: full update");
  }
}
