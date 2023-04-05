// Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

#include <button.h>
#include <pico/stdlib.h>
#include <hardware/structs/ioqspi.h>
#include <hardware/sync.h>

// Temporarily changes pin 25 to be an input in order to read button A.
bool button_a_is_pressed()
{
  gpio_set_oeover(25, GPIO_OVERRIDE_LOW);
  sleep_us(1);
  bool r = !gpio_get(25);
  gpio_set_oeover(25, GPIO_OVERRIDE_NORMAL);
  return r;
}

// Temporarily changes the QSPI_SS_N/BOOTSEL to be an input to read button B.
// While we are reading the button, we cannot execute any code from flash, so
// that is why we this function disables interrupts and writes directly to
// hardware registers (or calls inline functions).
bool __no_inline_not_in_flash_func(button_b_is_pressed)()
{
  uint32_t flags = save_and_disable_interrupts();

  hw_write_masked(&ioqspi_hw->io[1].ctrl,
                  GPIO_OVERRIDE_LOW << IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_LSB,
                  IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_BITS);

  // Delay for 1 to 2 us.
  uint32_t start = timer_hw->timerawl;
  while ((uint32_t)(timer_hw->timerawl - start) < 2);

  bool r = !(sio_hw->gpio_hi_in & (1 << 1));

  hw_clear_bits(&ioqspi_hw->io[1].ctrl, IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_BITS);

  restore_interrupts(flags);

  return r;
}

// Temporarily changes pin 0 to be an input in order to read button C.
bool button_c_is_pressed()
{
  gpio_set_oeover(0, GPIO_OVERRIDE_LOW);
  gpio_pull_up(0);
  sleep_us(1);
  bool r = !gpio_get(0);
  gpio_set_oeover(0, GPIO_OVERRIDE_NORMAL);
  return r;
}

int button_check(button * self)
{
  uint8_t s = self->is_pressed();
  uint32_t t = time_us_32();
  if (s != self->last_event && (uint32_t)(t - self->last_event_time) > self->debounce_us)
  {
    int edge = s - self->last_event;
    self->last_event = s;
    self->last_event_time = t;
    return edge;
  }
  return 0;
}
