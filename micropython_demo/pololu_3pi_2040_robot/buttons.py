from machine import Pin
import machine
import rp2
from time import ticks_us, sleep_us, ticks_diff

class Button():
    def __init__(self):
        # Initialize to the current pressed/not-pressed state
        # so that check() will not immediately return True.
        self.last_event = self.is_pressed()
        self.last_event_t = ticks_us()

        # Ensure that is_long_pressed() does not immediately return True.
        self.not_pressed_t = ticks_us()

        # configurable parameters
        self.debounce_ms = 10
        self.long_press_ms = 750

    # Call this method periodically to check for long presses.
    # Returns True if the button has been held down for
    # more than long_press_ms milliseconds.
    def is_long_pressed(self):
        if not self.is_pressed():
            self.not_pressed_t = ticks_us()
        elif self.not_pressed_t is not None:
            if ticks_diff(ticks_us(), self.not_pressed_t) > self.long_press_ms * 1000:
                self.not_pressed_t = None
        return self.not_pressed_t is None

    # Call this method periodically to check for debounced button events.
    # Returns True once for each button press.
    # Returns False once for each button release.
    # Returns None if there is no new event.
    def check(self):
        if self.last_event_t is not None:
            if ticks_diff(ticks_us(), self.last_event_t) > self.debounce_ms * 1000:
                self.last_event_t = None
        if self.last_event_t is None:
            s = self.is_pressed()
            if s != self.last_event:
                self.last_event = s
                self.last_event_t = ticks_us()
                return s

class ButtonA(Button):
    def is_pressed(self):
        ctrl = machine.mem32[0x400140cc]
        machine.mem32[0x400140cc] = ctrl & ~(0x1 << 12) | 0x1 << 13
        sleep_us(1)
        ret = 0x1 & machine.mem32[0x400140c8] >> 17
        machine.mem32[0x400140cc] = ctrl
        return not ret

class ButtonB(Button):
    def is_pressed(self):
        return rp2.bootsel_button() == 1

class ButtonC(Button):
    def __init__(self):
        self.pin = Pin(0)
        super().__init__()

    def is_pressed(self):
        self.pin.init(Pin.IN, Pin.PULL_UP)
        ret = self.pin.value()

        # keep this pin low by default
        Pin(0).init(Pin.OUT, value=0)
        return not ret
