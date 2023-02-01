import time
import rp2
from machine import Pin

led = Pin(25, Pin.OUT)
button_b = Pin(3, Pin.IN, Pin.PULL_UP)

while True:
    led.off()
    time.sleep_ms(100)
    led.on()
    time.sleep_ms(600)