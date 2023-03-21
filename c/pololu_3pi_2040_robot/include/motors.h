// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file motors.h
/// This header functions for controlling the robot's motors.

#pragma once

#include <stdbool.h>
#include <stdint.h>

/// The motor speeds accepted by this library range from -6000 to 6000.
#define MOTORS_MAX_SPEED 6000

/// This should be called before calling any other motor functions.
void motors_init(void);

/// Specifies whether to flip direction of the left motor or not.
void motors_flip_left(bool flip);

/// Specifies whether to flip direction of the left motor or not.
void motors_flip_right(bool flip);

/// @brief Sets the speed of the left motor.
///
/// @param speed A number between -6000 and 6000.
///   Values outside this range are treated as the nearest valid speed.
void motors_set_left_speed(int32_t speed);

/// @brief Sets the speed of the right motor.
///
/// @param speed A number between -6000 and 6000.
///   Values outside this range are treated as the nearest valid speed.
void motors_set_right_speed(int32_t speed);

/// Sets the speeds of both motors at the same time.
void motors_set_speeds(int32_t left_speed, int32_t right_speed);
