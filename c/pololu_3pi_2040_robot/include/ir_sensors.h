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

/// Starts a reading of the down-facing line sensors on the robot.
///
/// This function turns on the down-facing infrared emitters and also turns off
/// the bump sensor emitters.
///
/// You can get the results of the reading later by calling line_sensors_read().
void line_sensors_start_read(void);

/// Reads the down-facing line sensors on the robot.
///
/// This function turns on the down-facing infrared emitters while reading
/// and also turns off the bump sensor emitters.
///
/// The readings are stored in the line_sensors array.
/// A higher reading indicates less light was reflected.
void line_sensors_read(void);

/// Starts a reading of the bump sensors on the front of the robot.
///
/// This function turns on the bump sensor infrared emitters and also turns off
/// the down-facing line sensor emitters.
///
/// You can get the results of the reading later by calling line_sensors_read().
void bump_sensors_start_read(void);

/// Reads the bump sensors on the front of the robot.
///
/// This function turns on the bump sensor infrared emitters while reading
/// and also turns off the down-facing line sensor emitters.
///
/// The readings are stored in bump_sensor_left and bump_sensor_right.
/// A higher reading indicates less light was reflected, and corresponds to an
/// object pressing on the corresponding plastic flap on the front of the robot.
void bump_sensors_read(void);

