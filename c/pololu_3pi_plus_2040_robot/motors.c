// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <pololu_3pi_plus_2040_robot.h>
#include <hardware/gpio.h>
#include <hardware/pwm.h>

static bool motors_flip_left = false;
static bool motors_flip_right = false;

void motors_init()
{
  gpio_init(10);
  gpio_init(11);
  gpio_set_dir(10, GPIO_OUT);
  gpio_set_dir(11, GPIO_OUT);

  gpio_set_function(14, GPIO_FUNC_PWM);
  gpio_set_function(15, GPIO_FUNC_PWM);

  // PWM frequency = 125 MHz / 1 / 6000 = 20.8 kHz
  pwm_set_clkdiv_int_frac(7, 1, 0);
  pwm_set_wrap(7, MOTORS_MAX_SPEED - 1);
  pwm_set_enabled(7, true);
}

void motors_flip(bool flip_left, bool flip_right)
{
  motors_flip_left = flip_left;
  motors_flip_right = flip_right;
}

void motors_set_speeds(int32_t left_speed, int32_t right_speed)
{
  if (left_speed < 0)
  {
    if (left_speed < -MOTORS_MAX_SPEED) { left_speed = -MOTORS_MAX_SPEED; }
    gpio_put(11, !motors_flip_left);
    left_speed = -left_speed;
  }
  else
  {
    if (left_speed > MOTORS_MAX_SPEED) { left_speed = MOTORS_MAX_SPEED; }
    gpio_put(11, motors_flip_left);
  }

  if (right_speed < 0)
  {
    if (right_speed < -MOTORS_MAX_SPEED) { right_speed = -MOTORS_MAX_SPEED; }
    gpio_put(10, !motors_flip_right);
    right_speed = -right_speed;
  }
  else
  {
    if (right_speed > MOTORS_MAX_SPEED) { right_speed = MOTORS_MAX_SPEED; }
    gpio_put(10, motors_flip_right);
  }

  pwm_set_both_levels(7, right_speed, left_speed);
}
