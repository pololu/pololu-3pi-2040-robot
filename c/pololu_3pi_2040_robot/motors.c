// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <motors.h>
#include <hardware/gpio.h>
#include <hardware/pwm.h>

static bool flip_left_motor = false;
static bool flip_right_motor = false;

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
  motors_set_speeds(0, 0);
}

void motors_flip_left(bool flip)
{
  flip_left_motor = flip;
}

void motors_flip_right(bool flip)
{
  flip_right_motor = flip;
}

static uint16_t set_dir_left(int32_t speed)
{
  if (speed < 0)
  {
    if (speed < -MOTORS_MAX_SPEED) { speed = -MOTORS_MAX_SPEED; }
    gpio_put(11, !flip_left_motor);
    return -speed;
  }
  else if (speed > 0)
  {
    if (speed > MOTORS_MAX_SPEED) { speed = MOTORS_MAX_SPEED; }
    gpio_put(11, flip_left_motor);
    return speed;
  }
  return 0;
}

static uint16_t set_dir_right(int32_t speed)
{
  if (speed < 0)
  {
    if (speed < -MOTORS_MAX_SPEED) { speed = -MOTORS_MAX_SPEED; }
    gpio_put(10, !flip_right_motor);
    return -speed;
  }
  else if (speed > 0)
  {
    if (speed > MOTORS_MAX_SPEED) { speed = MOTORS_MAX_SPEED; }
    gpio_put(10, flip_right_motor);
    return speed;
  }
  return 0;
}

void motors_set_left_speed(int32_t speed)
{
  pwm_set_chan_level(7, 1, set_dir_left(speed));
}

void motors_set_right_speed(int32_t speed)
{
  pwm_set_chan_level(7, 0, set_dir_right(speed));
}

void motors_set_speeds(int32_t left_speed, int32_t right_speed)
{
  pwm_set_both_levels(7, set_dir_right(right_speed), set_dir_left(left_speed));
}
