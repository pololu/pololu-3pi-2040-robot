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

  uint32_t start;

  while (1)
  {
    putchar('\n');

    start = time_us_32();
    display_fill(0);
    display_show();
    report(time_us_32() - start, "Clear");

    display_set_font(font_8x16);

    // TODO: 8x16 full update

    start = time_us_32();
    display_text("hi:)", 0, 0, DISPLAY_NOW);
    report(time_us_32() - start, "8x16: 4-char ASCII update");

    start = time_us_32();
    display_text("hello world :):)", 0, 0, DISPLAY_NOW);
    report(time_us_32() - start, "8x16: 16-char ASCII update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→𝟅", 4, 24, DISPLAY_NOW);
    report(time_us_32() - start, "8x16: 16-char Unicode update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→𝟅", 4, 24, 0);
    report(time_us_32() - start, "8x16: 16-char Unicode render");

    display_set_font(font_8x8);
    display_fill(0);
    display_show();

    // TODO: 8x8 full update

    start = time_us_32();
    display_text("hi:)", 0, 0, DISPLAY_NOW);
    report(time_us_32() - start, "8x8: 4-char ASCII update");

    start = time_us_32();
    display_text("hello world :):)", 0, 0, DISPLAY_NOW);
    report(time_us_32() - start, "8x8: 16-char ASCII update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→𝟅", 4, 8, DISPLAY_NOW);
    report(time_us_32() - start, "8x8: 16-char Unicode update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ…←↑→𝟅", 4, 8, 0);
    report(time_us_32() - start, "8x8: 16-char Unicode render");
  }
}
