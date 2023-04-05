# Demonstrates the IR sensors on the 3pi+ robot: the left and right
# bump sensors on the front of the robot and the five downward-looking
# reflectance/line sensors.
#
# Press A to calibrate both sets of sensors.
#
# Press C to switch the line sensors to display calibrated or
# uncalibrated values.

from pololu_3pi_2040_robot import robot
import time

line_sensors = robot.LineSensors()
bump_sensors = robot.BumpSensors()
display = robot.Display()
last_update = 0
button_a = robot.ButtonA()
button_c = robot.ButtonC()

calibrate = 0
use_calibrated_read = False

while True:
    bump = bump_sensors.read()

    # Start a background read; we'll time how long the
    # non-blocking part takes later.
    line_sensors.start_read()

    # In a real program you could do slow things while
    # waiting for the sensors.
    time.sleep_ms(2)

    if use_calibrated_read and not calibrate:
        start = time.ticks_us()
        line = line_sensors.read_calibrated()
        stop = time.ticks_us()
    else:
        start = time.ticks_us()
        line = line_sensors.read()
        stop = time.ticks_us()

    if calibrate == 1:
        line_sensors.calibrate()

    if stop - last_update > 200000:
        last_update = stop

        display.fill_rect(0, 0, 128, 30, 0)

        if use_calibrated_read:
            display.text("Calibrated {}us".format(stop-start), 0, 0)
        else:
            display.text("Uncalib.   {}us".format(stop-start), 0, 0)
        if calibrate == 0:
            display.text('A: calibrate', 0, 10)
            display.text('C: switch mode', 0, 20)
        elif calibrate == 1:
            display.text('cal line sens...', 0, 10)
            display.text('A: stop', 0, 20)

    if button_a.check():
        last_update = 0 # force display refresh
        if calibrate == 0:
            bump_sensors.calibrate()
            display.fill_rect(0, 10, 128, 20, 0)
            display.text('calibrated bump', 0, 10)
            display.text('sensors...', 0, 20)
            display.show()
            time.sleep_ms(500)

            calibrate = 1 # calibrate line sensors
        else:
            calibrate = 0

    if button_c.check():
        last_update = 0
        use_calibrated_read = not use_calibrated_read

    # 64-40 = 24
    scale = 24/1023

    display.fill_rect(0, 32, 128, 32, 0)

    if bump_sensors.left_is_pressed():
        display.fill_rect(0, 64-int(bump[0]*scale), 8, int(bump[0]*scale), 1)
    else:
        display.rect(0, 64-int(bump[0]*scale), 8, int(bump[0]*scale), 1)

    display.fill_rect(36, 64-int(line[0]*scale), 8, int(line[0]*scale), 1)
    display.fill_rect(48, 64-int(line[1]*scale), 8, int(line[1]*scale), 1)
    display.fill_rect(60, 64-int(line[2]*scale), 8, int(line[2]*scale), 1)
    display.fill_rect(72, 64-int(line[3]*scale), 8, int(line[3]*scale), 1)
    display.fill_rect(84, 64-int(line[4]*scale), 8, int(line[4]*scale), 1)

    if bump_sensors.right_is_pressed():
        display.fill_rect(120, 64-int(bump[1]*scale), 8, int(bump[1]*scale), 1)
    else:
        display.rect(120, 64-int(bump[1]*scale), 8, int(bump[1]*scale), 1)

    display.show()
