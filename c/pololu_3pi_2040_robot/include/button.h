// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

/// @file button.h
/// Functions for accessing the pushbuttons on the control board.

#include <stdbool.h>
#include <stdint.h>

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

typedef struct button {
  /// A pointer to the function for reading the button state.
  bool (*is_pressed)(void);

  /// The number of microseconds to require between events (configurable).
  uint32_t debounce_us;

  /// The time of the last event, from ticks_us_32().
  uint32_t last_event_time;

  /// 1 for pressed, 0 for not
  uint8_t last_event;
} button;

/// Initializes the provided button struct to track the state of button A.
void button_a_init(button *);

/// Initializes the provided button struct to track the state of button B.
void button_b_init(button *);

/// Initializes the provided button struct to track the state of button C.
void button_c_init(button *);

/// @brief Checks for a debounced button press or release event.
///
/// @return 0 if no event happened, -1 if the button was released,
/// 1 if it was pressed.
int button_check(button * button);
