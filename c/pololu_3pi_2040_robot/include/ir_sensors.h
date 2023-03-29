// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file ir_sensors.h
/// This header provides functions for reading the robot's infrared
/// line and bump sensors.
///
/// These functions use a state machine of the RP2040's PIO1 module and
/// 12 instructions in its program memory.

#pragma once

#include <stdint.h>
#include <stdbool.h>

/// The latest raw readings from the down-facing line sensors.
///
/// The first element corresponds to the left sensor.
/// The readings are between 0 and 1024, with higher readings corresponding to
/// less light being reflected.
/// The line_sensors_read() function updates this array.
extern uint16_t line_sensors[5];

/// Minimum sensor values detected during line sensor calibration.
/// Raw readings at this level or below are mapped to 0.
extern uint16_t line_sensors_cal_min[5];

/// Maximum sensor values detected during line sensor calibration.
/// Raw readings at this level or above are mapped to 1000.
extern uint16_t line_sensors_cal_max[5];

/// The latest calibrated readings from the down-facing line sensors.
///
/// The first element corresponds to the left sensor.
/// These readings are between 0 and 1000, with higher readings corresponding to
/// less light being reflected.
/// The line_sensors_read_calibrated() function updates this array.
extern uint16_t line_sensors_calibrated[5];

/// The latest raw readings from the bump sensors.
///
/// The first element corresponds to the left sensor.
/// The readings are between 0 and 1024, with higher readings corresponding to
/// less light being reflected.
/// The bump_sensors_read() function updates this array.
extern uint16_t bump_sensors[2];

/// Bump sensor lower thresholds calculated during calibration.
///
/// The first element corresponds ot the left sensor.
///
/// If the bump sensor is currently considered to be pressed, the bump sensor
/// raw reading has to drop below this level before it is considered to be
/// not pressed.
extern uint16_t bump_sensors_threshold_min[2];

/// Bump sensor higher thresholds calculated during calibration.
///
/// The first element corresponds ot the left sensor.
///
/// If the bump sensor is currently considered to be not pressed, the bump
/// sensor raw reading has to rise above this level before it is considered to
/// be pressed.
extern uint16_t bump_sensors_threshold_max[2];

/// The latest calibrated readings from the bump sensors.
///
/// Each value is 1 if the corresponding bump sensor is considered to be
/// pressed and 0 otherwise.
/// The bump_sensors_read() function updates this array.
extern bool bump_sensors_pressed[2];

/// Resets the line sensor calibration to its initial state.
/// In this state, all the calibrated readings are 0.
void line_sensors_reset_calibration(void);

/// Reads the line sensors 10 times to update the calibration.
///
/// The general procedure for line sensor calibration is to call this function
/// repeatedly while exposing the line sensors to the brightest and darkest
/// surfaces they are expected to sense.
///
/// This function updates the arrays line_sensors_cal_min and
/// line_sensors_cal_max.
void line_sensors_calibrate(void);

/// Starts a reading of the down-facing line sensors on the robot.
///
/// This function turns on the down-facing infrared emitters and also turns off
/// the bump sensor emitters.
///
/// You can get the results of the reading by calling line_sensors_read() at a
/// later time.
void line_sensors_start_read(void);

/// Reads the down-facing line sensors on the robot.
///
/// This function turns on the down-facing infrared emitters while reading
/// and also turns off the bump sensor emitters.
///
/// The readings are stored in the line_sensors array.
void line_sensors_read(void);

/// Reads the down-facing line sensors on the robot and calculates calibrated
/// readings for them.
///
/// This function calls line_sensors_read() and also updates the
/// line_sensors_calibrated array.
///
/// The calibated readings will only be valid if the line sensors have been
/// calibrated: see line_sensors_calibrate().
void line_sensors_read_calibrated(void);

/// Resets the bump sensor calibration to its initial state.
/// In this state, all bump sensors are reported as not pressed.
void bump_sensors_reset_calibration(void);

/// Reads the bump sensors 50 times and sets the calibration.
///
/// The procedure for bump sensor calibration is to call this function once
/// while the bump sensors are not pressed.
///
/// This function updates the array bump_sensors_threshold.
void bump_sensors_calibrate(void);

/// Starts a reading of the bump sensors on the front of the robot.
///
/// This function turns on the bump sensor infrared emitters and also turns off
/// the down-facing line sensor emitters.
///
/// You can get the results of the reading by calling bump_sensors_read() at a
/// later time.
void bump_sensors_start_read(void);

/// Reads the bump sensors on the front of the robot.
///
/// This function turns on the bump sensor infrared emitters while reading
/// and also turns off the down-facing line sensor emitters.
///
/// The raw readings are stored in the bump_sensors array.
/// A higher reading indicates less light was reflected, and corresponds to an
/// object pressing on the corresponding plastic flap on the front of the robot.
///
/// Additionally, this function updates the bump_sensors_pressed array.
/// That array will only be valid if the bump sensors have been calibrated:
/// see bump_sensors_calibrate().
void bump_sensors_read(void);

/// Just returns bump_sensors_pressed[0].
/// This value is updated when you call bump_sensors_read().
bool bump_sensor_left_is_pressed(void);

/// Just returns bump_sensors_pressed[1].
/// This value is updated when you call bump_sensors_read().
bool bump_sensor_right_is_pressed(void);
