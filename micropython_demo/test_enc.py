import pololu_3pi_plus_2040_robot as robot

led = robot.YellowLED()
encoders = robot.Encoders()
display = robot.Display()

while True:
    c = encoders.get_counts()
    led((c[0] + c[1]) % 2)
    display.fill_rect(0, 0, 128, 18, 0)
    display.text("Left: "+str(c[0]), 0, 0)
    display.text("Right: "+str(c[1]), 0, 10)
    display.show()