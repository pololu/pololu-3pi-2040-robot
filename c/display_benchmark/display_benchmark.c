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
  sh1106_page_write(page, data);
}

void report(uint32_t time, const char * name)
{
  size_t name_length = printf("%s: ", name);
  for (size_t i = name_length; i < 32; i++) { putchar(' '); }
  printf("%ld\n", time);

  sleep_ms(1000);
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

    display_fill(0);

    start = time_us_32();
    display_text("hello :)", 0, 0, 0);
    display_show();
    report(time_us_32() - start, "8-character ASCII update");

    start = time_us_32();
    display_text("°±²µΔΘΩθμπ←↑→↓𝟅𝟅", 0, 16, 0);
    display_show();
    report(time_us_32() - start, "16-character unicode update");

    start = time_us_32();
    sh1106_transfer_start();
    show_bar(0, 10);
    show_bar(1, 20);
    show_bar(2, 30);
    show_bar(3, 40);
    show_bar(4, 50);
    show_bar(5, 60);
    show_bar(6, 70);
    show_bar(7, 80);
    sh1106_transfer_end();
    report(time_us_32() - start, "Full raw update");

    start = time_us_32();
    sh1106_clear();
    report(time_us_32() - start, "Clear");

    sleep_ms(1000);
  }
}
