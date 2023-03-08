# TODO: fix gyro sensitivtity so angle doesn't get messed up
# TODO: tune the PID parameters for standard edition
# TODO: make it work well on the other editions too (with a menu to select them?)
# TODO: clean up the code

# TODO: why does the angle get exteremely messed up if you pick up the robot, turn
# it, and put it down again?  I bet the gyro is saturating, so we need to pick
# better settings.

import time
from pololu_3pi_2040_robot import robot

#rgb_leds = robot.RGBLEDs()
motors = robot.Motors()
#buzzer = robot.Buzzer()
button_a = robot.ButtonA()
display = robot.Display()
yellow_led = robot.YellowLED()

imu = robot.IMU()
imu.reset()
imu.enable_default()

display.fill(0)
display.text("Calibrating...", 0, 0, 1)
display.show()
start = time.ticks_ms()
stationary_gz = 0.0
reading_count = 0
while time.ticks_diff(time.ticks_ms(), start) < 3000:
    imu.read()
    stationary_gz += imu.gyro.last_reading_dps[2]
    reading_count += 1
stationary_gz /= reading_count

drive_motors = False
last_time = None
angle = 0.0
while True:
    # Update the angle and the turn rate.
    imu.read()
    turn_rate = imu.gyro.last_reading_dps[2] - stationary_gz  # degrees per second
    now = time.ticks_us()
    if last_time:
      dt = time.ticks_diff(now, last_time) / 1000000
      angle += turn_rate * dt

    # If the user presses button A, toggle whether the motors are on.
    if button_a.check() == True:
        drive_motors = not drive_motors
        if drive_motors:
            display.fill(0)
            display.text("Starting motors!".format(angle), 0, 0, 1)
            display.show()
            time.sleep_ms(500)
            last_time = time.ticks_us()

    # Update the display
    display.fill(0)
    display.text("{:>5.1f}".format(angle), 0, 0, 1)
    display.show()
    last_time = now

    # Drive motors
    if drive_motors:
        speed = angle / 30 * motors.MAX_SPEED + turn_rate / 50
        if speed > 3000: speed = 3000
        if speed < -3000: speed = -3000
        motors.set_speeds(speed, -speed)
        yellow_led.on()
    else:
        motors.off()
        yellow_led.off()

# for i in range(0, max, step):
#     motors.set_speeds(i, -i)
#     time.sleep_ms(10)

# time.sleep_ms(500)

# for i in range(max, 0, -step):
#     motors.set_speeds(i, -i)
#     time.sleep_ms(15)

# for i in range(0, -max, -step):
#     motors.set_speeds(i, -i)
#     time.sleep_ms(15)

# time.sleep_ms(500)

# for i in range(-max, 0, step):
#     motors.set_speeds(i, -i)
#     time.sleep_ms(10)
