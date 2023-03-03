// This example shows how to control the motors on the Pololu 3pi+ 2040 Robot.
// It tests each motor by running it forward and then reverse with smooth
// acceleration and deceleration.

#include <stdio.h>
#include <pico/stdlib.h>
#include <pololu_3pi_2040_robot.h>

int main()
{
  stdio_init_all();
  motors_init();

  // If a motor on your 3pi+ is installed in a flipped orienation, you can
  // uncomment one or two lines below to have the library correct for it.
  //motors_flip_left(true);
  //motors_flip_right(true);

  while (1)
  {
    int32_t speed;

    printf("Left forward\n");
    speed = 0;
    while (speed <= MOTORS_MAX_SPEED)
    {
      motors_set_left_speed(speed);
      sleep_ms(1);
      speed += 10;
    }
    while (speed >= 0)
    {
      motors_set_left_speed(speed);
      sleep_ms(1);
      speed -= 10;
    }
    motors_set_speeds(0, 0);
    sleep_ms(250);

    printf("Left reverse\n");
    speed = 0;
    while (speed >= -MOTORS_MAX_SPEED)
    {
      motors_set_left_speed(speed);
      sleep_ms(1);
      speed -= 10;
    }
    while (speed <= 0)
    {
      motors_set_left_speed(speed);
      sleep_ms(1);
      speed += 10;
    }
    motors_set_speeds(0, 0);
    sleep_ms(250);

    printf("Right forward\n");
    speed = 0;
    while (speed <= MOTORS_MAX_SPEED)
    {
      motors_set_right_speed(speed);
      sleep_ms(1);
      speed += 10;
    }
    while (speed >= 0)
    {
      motors_set_right_speed(speed);
      sleep_ms(1);
      speed -= 10;
    }
    motors_set_speeds(0, 0);
    sleep_ms(250);

    printf("Right reverse\n");
    speed = 0;
    while (speed >= -MOTORS_MAX_SPEED)
    {
      motors_set_right_speed(speed);
      sleep_ms(1);
      speed -= 10;
    }
    while (speed <= 0)
    {
      motors_set_right_speed(speed);
      sleep_ms(1);
      speed += 10;
    }
    motors_set_speeds(0, 0);
    sleep_ms(250);
  }
}
