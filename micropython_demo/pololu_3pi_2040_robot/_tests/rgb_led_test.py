# Run this test to verify that the LED functions work properly.

from pololu_3pi_2040_robot import robot

leds = robot.RGBLEDs()

assert leds.get_brightness() == 31

leds.set_brightness(5)

assert leds.get_brightness() == 5
assert leds.get_brightness(5) == 5

leds.set_brightness(10, 5)

assert leds.get_brightness(0) == 5
assert leds.get_brightness(5) == 10

leds.set(0, [10, 20, 30])
assert leds.get(0) == [10, 20, 30]

leds.off()
assert leds.get(0) == [0, 0, 0]
assert leds.get_brightness(0) == 5
assert leds.get_brightness(5) == 10

leds.set_hsv(0, [0, 255, 255])
leds.set_hsv(1, [60, 255, 255])
leds.set_hsv(2, [120, 255, 255])
leds.set_hsv(3, [180, 255, 255])
leds.set_hsv(4, [240, 255, 255])
leds.set_hsv(5, [300, 255, 255])
assert leds.get(0) == [255, 0, 0]
assert leds.get(1) == [255, 255, 0]
assert leds.get(2) == [0, 255, 0]
assert leds.get(3) == [0, 255, 255]
assert leds.get(4) == [0, 0, 255]
assert leds.get(5) == [255, 0, 255]

leds.set_hsv(5, [300, 128, 255])
assert leds.get(5) == [255, 127, 255]

leds.set_hsv(5, [300, 255, 128])
assert leds.get(5) == [128, 0, 128]

leds.set_hsv(5, [129, 255, 255], h_scale=256)
assert leds.get(5) == [0, 255, 255]