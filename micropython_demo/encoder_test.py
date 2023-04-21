# Displays encoder counts on the screen and blinks the yellow LED with
# each tick.

from pololu_3pi_2040_robot import robot

led = robot.YellowLED()
encoders = robot.Encoders()
display = robot.Display()
buttonB = robot.ButtonB()

while True:
    c = encoders.get_counts()

    # change LED on every count
    led((c[0] + c[1]) % 2)

    display.fill_rect(0, 0, 128, 18, 0)
    display.text("Left: "+str(c[0]), 0, 0)
    display.text("Right: "+str(c[1]), 0, 10)
    display.text("Press B to reset", 0, 30)
    display.show()

    if buttonB.check():
        encoders.get_counts(reset = True)
