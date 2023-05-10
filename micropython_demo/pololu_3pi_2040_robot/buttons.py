from machine import Pin
import machine
import rp2
from time import ticks_us, sleep_us

class Button():
    def __init__(self):
        self.last_event = False
        self.last_t = ticks_us() - 10*1000*1000
        self.debounce_ms = 10 # configurable

    def check(self):
        s = self.is_pressed()
        t = ticks_us()
        if s != self.last_event and t - self.last_t > self.debounce_ms*1000:
            self.last_event = s
            self.last_t = t
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
