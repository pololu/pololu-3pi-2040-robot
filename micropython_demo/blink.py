# Simple blink example

import time
from machine import Pin

led = Pin(25, Pin.OUT)

while True:
    led.value(0)  # yellow LED on
    time.sleep_ms(100)
    led.value(1)  # yellow LED off
    time.sleep_ms(600)
