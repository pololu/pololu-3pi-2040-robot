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
# immediately.  In this case you can still hold B or C
# on startup to activate the associated function.
# (Holding A on startup starts self_test.py.)
#
# If your default program exits normally, this script
# will try to shut off the RGB LEDs, motors, and
# buzzer.  If it raises an exception, it will be
# shown on the screen.  You can get more details about
# the exception from the REPL by running:
#   sys.print_exception(exc)
#
# If you don't need these features, you can of course
# replace this script with your own main.py.

try:
    from pololu_3pi_2040_robot.extras.splash_loader import splash_loader
    splash_loader(
        default_program = None, # "my_program.py"
        splash_delay_s = 6, # delay while waiting for a button
        run_file_delay_ms = 700 # extra delay to show the action
        )

except Exception as e:
    from pololu_3pi_2040_robot.motors import Motors
    Motors()   # turn off Motors ASAP
    exc = e    # enable access to original exception in REPL
    from pololu_3pi_2040_robot.rgb_leds import RGBLEDs
    RGBLEDs()  # turn off RGB LEDs
    from pololu_3pi_2040_robot.buzzer import Buzzer
    buzzer = Buzzer()

    from pololu_3pi_2040_robot.display import Display
    Display.show_exception(e)
    buzzer.play("O2c4")
    raise

finally:
    from pololu_3pi_2040_robot.motors import Motors
    Motors()   # turn off Motors ASAP
    from pololu_3pi_2040_robot.buzzer import Buzzer
    Buzzer()   # turn off Buzzer
    from pololu_3pi_2040_robot.rgb_leds import RGBLEDs
    RGBLEDs()  # turn off RGB LEDs

    # don't leave extra classes lying around
    del Motors, Buzzer, RGBLEDs, splash_loader

    # make the REPL friendlier, if you enter it the right way
    from pololu_3pi_2040_robot import robot
    import sys
