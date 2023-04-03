# This demo spins the robot in place by driving one motor forward and
# the other back, while playing a tune on the buzzer.

from pololu_3pi_2040_robot import robot
import time

rgb_leds = robot.RGBLEDs()
motors = robot.Motors()
buzzer = robot.Buzzer()
display = robot.Display()

display.fill(1)
display.text("Spinning", 30, 20, 0)
display.text("WATCH OUT", 27, 30, 0)
display.show()

buzzer.play("L16 o4 cfa>cra>c4r4")

circus =\
    "! O6 L8 T180" +\
    "MS aa- L16 ML ga-gg- L8 MS fe ML e- MS e fe L16 ML e-ee-d L8 MS d-c ML <b MS c" +\
    "MS e L16 <b<b L8 ML <b-<b" +\
    "MS e L16 <b<b L8 ML <b-<b" +\
    "L16 <a-<a<b-<bcd-de- L8 MS fe ML e- MS e"

rgb_leds.set(0, [255, 0, 0])
rgb_leds.set(1, [192, 64, 0])
rgb_leds.set(2, [128, 128, 0])
rgb_leds.set(3, [0, 255, 0])
rgb_leds.set(4, [0, 0, 255])
rgb_leds.set(5, [128, 0, 128])
rgb_leds.show()

buzzer.play_in_background(circus)

max = motors.MAX_SPEED
step = max // 100

for i in range(0, max, step):
    motors.set_speeds(i, -i)
    time.sleep_ms(10)

time.sleep_ms(500)

for i in range(max, 0, -step):
    motors.set_speeds(i, -i)
    time.sleep_ms(15)

for i in range(0, -max, -step):
    motors.set_speeds(i, -i)
    time.sleep_ms(15)

time.sleep_ms(500)

for i in range(-max, 0, step):
    motors.set_speeds(i, -i)
    time.sleep_ms(10)

display.fill(0)
display.show()
motors.off()
rgb_leds.off()
buzzer.off()



