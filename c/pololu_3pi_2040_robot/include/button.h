// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file button.h
/// Functions for accessing the pushbuttons on the control board.

#include <stdbool.h>

/// Returns 1 if button A is pressed, or 0 otherwise.
bool button_a_is_pressed(void);

/// Returns 1 if button B is pressed, or 0 otherwise.
///
/// This function temporarily changes QSPI_SS_N/BOOTSEL to be an input, so it
/// disrupts all access to the flash memory chip.  This function temporarily
/// disables interrupts, but it does nothing to prevent the other core from
/// accesssing flash, so it should not be used in multi-core applications.
///
/// (The Micropython rp2.bootsel_button() method does disable both cores.)
bool button_b_is_pressed(void);

/// Returns 1 if button C is pressed, or 0 otherwise.
bool button_c_is_pressed(void);
