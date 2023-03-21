// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file ir_sensors.h
/// This header provides functions for reading the robot's infrared
/// line and bump sensors.
///
/// These functions use a state machine of the RP2040's PIO1 module and
/// 12 instructions in its program memory.

#pragma once

#include <stdint.h>

/// The latest reading from the left bump sensor.  See ir_sensors_read_bump().
extern uint16_t bump_sensor_left;

/// The latest reading from the right bump sensor.  See ir_sensors_read_bump().
extern uint16_t bump_sensor_right;

/// The latest readings from the down-facing line sensors.
/// See ir_sensors_read_line().
extern uint16_t line_sensors[5];

/// Reads the bump sensors on the front of the 3pi+ robot.
///
/// While reading, this function turns on the emitters by driving
/// GP23 high.
///
/// The readings are stored in bump_sensor_left and bump_sensor_right.
/// A higher reading indicates less light was reflected, and corresponds to an
/// object pressing on the corresponding plastic flap on the front of the robot.
void ir_sensors_read_bump(void);

/// Reads the line sensors facing down on the 3pi+ robot.
///
/// While reading, this function turns on the emitters by driving
/// GP26 high.
///
/// The readings are stored in the line_sensors array.
/// A higher reading indicates less light was reflected.
void ir_sensors_read_line(void);
