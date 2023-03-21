// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file pololu_3pi_2040_robot.h
///
/// This is the main header file for the C library for the
/// Pololu 3pi+ 2040 Robot.

#pragma once

#include <stdbool.h>
#include "button.h"
#include "display.h"
#include "ir_sensors.h"
#include "motors.h"
#include "rgb_leds.h"
#include "sh1106.h"

/// Turns the yellow LED on if the argument is 1, or off if the argument is 0.
void yellow_led(bool);

/// Performs an ADC reading and calculates the battery level (VSW),
/// in millivolts.
uint16_t battery_get_level_millivolts(void);
