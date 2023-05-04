# This example shows how to read the buttons on the Pololu 3pi+ 2040 Robot.
# This includes the three pushbuttons on the control board and the two bump
# sensors on the front of the robot, which can be used as buttons.
#
# The bump sensors are calibrated when the program starts running: they should
# not be pressed at that time in order to get an accurate calibration.
#
# This demo configures button A with an unusually high debounce time of 500 ms
# so you can see the debouncing effect by pressing the button quickly.

from pololu_3pi_2040_robot import robot

display = robot.Display()
button_a = robot.ButtonA()
button_a.debounce_ms = 500
button_b = robot.ButtonB()
button_c = robot.ButtonC()
bump_sensors = robot.BumpSensors()
bump_sensors.calibrate()

buffer = ""

while True:
    bump_sensors.read()

    display.fill(0)
    display.text("A:" + str(button_a.is_pressed()), 0, 0)
    display.text("B:" + str(button_b.is_pressed()), 0, 8)
    display.text("C:" + str(button_c.is_pressed()), 0, 16)
    display.text("L:" + str(bump_sensors.left.is_pressed()), 64, 0)
    display.text("R:" + str(bump_sensors.right.is_pressed()), 64, 8)

    if button_a.check(): buffer += "A"
    if button_b.check(): buffer += "B"
    if button_c.check(): buffer += "C"
    if bump_sensors.left.check(): buffer += "L"
    if bump_sensors.right.check(): buffer += "R"

    if len(buffer) > 16:
        buffer = buffer[16:]
    display.text("Debounced output", 0, 28)
    display.text("with A at 500ms:", 0, 36)
    display.text(buffer, 0, 48)

    display.show()
