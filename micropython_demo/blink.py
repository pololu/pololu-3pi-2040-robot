# Simple blink example
# Hold Button B (BOOTSEL) to exit

import time
import rp2
from machine import Pin

led = Pin(25, Pin.OUT)

while True:
    led.value(0)  # yellow LED on
    time.sleep_ms(100)
    led.value(1)  # yellow LED off
    time.sleep_ms(600)

    # check for Button B at the end of the loop
    if rp2.bootsel_button() == 1:
        break
