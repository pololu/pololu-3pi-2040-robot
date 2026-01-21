# This demo shows when happens when you raise an exception. When you
# run it from main_menu.py, the exception text will print to the screen,
# and the buzzer will sound a low tone.

from pololu_3pi_2040_robot import robot

display = robot.Display()
buttonA = robot.ButtonA()
buttonB = robot.ButtonB()

while True:
    display.fill_rect(0, 0, 128, 18, 0)
    display.text("Press A to raise", 0, 0)
    display.text("exception", 0, 8)
    display.text("Press B to exit", 0, 56)
    display.show()

    if buttonA.check():
        raise Exception("This is a test exception.")
    if buttonB.check():
        break


