# Pololu 3pi+ 2040 Robot default main.py
#
# This script displays the logo screen and gives you
# several options to proceed:
#
# Button A: exit (and return to the REPL)
# Button B: launch the built-in UF2 bootloader
# Button C: select a top-level Python file to run
#
# If nothing is pressed, after a specified delay time,
# a default program runs.  You can customize the
# default program and delay times below.
#
# Setting the delays both to zero will eliminate the
# splash screen and initial beep, running your program
# immediately.  In this case you can still hold A, B,
# or C on startup to activate the associated function.
#
# If your default program exits normally, this script
# will try to shut off the RGB LEDs, motors, and
# buzzer.  If it raises an exception, it will be
# shown on the screen.
#
# If you don't need these features, you can of course
# replace this script with your own main.py.

import pololu_3pi_plus_2040_robot as robot

try:
    from pololu_3pi_plus_2040_robot.extras.splash_loader import splash_loader
    splash_loader(
        default_program = "blink.py",
        splash_delay_s = 6, # delay while waiting for a button
        run_file_delay_ms = 700 # extra delay to show the action 
        )

except Exception as e:
    robot.Motors()   # turn off Motors ASAP
    robot.RGBLEDs()  # turn off RGB LEDs
    buzzer = robot.Buzzer()
    
    display = robot.Display()
    display.text(type(e).__name__+":", 0, 0, 1)
    msg = str(e)
    msglines = [msg[i:i+16] for i in range(0, len(msg), 16)]
    for i in range(len(msglines)):
        display.text(msglines[i], 0, 8*(i+1), 1)
    display.show()
    buzzer.play("O2c4")
    raise

finally:
    robot.Motors()   # turn off Motors ASAP
    robot.Buzzer()   # turn off Buzzer
    robot.RGBLEDs()  # turn off RGBLEDs