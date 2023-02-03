// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pico/stdlib.h>
#include <pololu_3pi_plus_2040_robot.h>

void yellow_led(bool b)
{
  gpio_init(25);
  gpio_set_dir(25, GPIO_OUT);
  gpio_put(25, !b);
}
