# Demonstrates reading buttons with the ButtonA, ButtonB, and ButtonC
# classes.  This demo configures ButtonA with an unusually high
# debounce time of 500 ms, so you can see the debouncing effect by
# pressing the button quickly.

from pololu_3pi_2040_robot import robot

display = robot.Display()
button_a = robot.ButtonA()
button_a.debounce_ms = 500
button_b = robot.ButtonB()
button_c = robot.ButtonC()

buffer = ""

while True:
    display.fill(0)
    display.text("A: "+str(button_a.is_pressed()), 0, 0)
    display.text("B: "+str(button_b.is_pressed()), 0, 8)
    display.text("C: "+str(button_c.is_pressed()), 0, 16)

    if button_a.check():
        buffer += "A"
    if button_b.check():
        buffer += "B"
    if button_c.check():
        buffer += "C"

    if len(buffer) > 16:
        buffer = buffer[16]
    display.text("Debounced output", 0, 28)
    display.text("with A at 500ms:", 0, 36)
    display.text(buffer, 0, 48)

    display.show()
