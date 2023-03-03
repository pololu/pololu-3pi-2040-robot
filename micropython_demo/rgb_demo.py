# Demonstrates smooth color cycling on the RGB LEDs.

from pololu_3pi_2040_robot import robot
import time
import math

rgb_leds = robot.RGBLEDs()
rgb_leds.set_brightness(5)

def rainbow(hue_start, hue_step, s, v):
    for led in range(6):
        r, g, b = rgb_leds.hsv2rgb(hue_start + hue_step * led, s, v)

        # Green is really bright relative to the other colors;
        # scaling it down 3x makes it look nicer.
        rgb_leds.set(led, [r, g//3, b])
    rgb_leds.show()

h = 0
while True:
    time_ms = time.ticks_us() // 1000
    rainbow(time_ms//8, 60, 230 + round(25*math.cos(time_ms/3000)), 255)
    time.sleep_ms(20)
