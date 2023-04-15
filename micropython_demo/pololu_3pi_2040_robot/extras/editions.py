# Functions for selecting what edition of the 3pi+ 2040 is being used:
# Standard, Turtle, or Hyper.

from pololu_3pi_2040_robot.extras.menu import Menu
from pololu_3pi_2040_robot.display import Display
from pololu_3pi_2040_robot.buttons import ButtonA, ButtonB, ButtonC
from pololu_3pi_2040_robot.buzzer import Buzzer

editions = [ "Standard", "Turtle", "Hyper" ]

# This function always attempts to read the "edition.conf" file to determine
# which choice to highlight by default.
# If 'remember' is True (the default), it also stores the user's answer in
# edition.conf.
def select(*, remember=True):
    menu = Menu(editions)
    menu.display = Display()
    menu.buzzer = Buzzer()
    menu.previous_button = ButtonA()
    menu.select_button = ButtonB()
    menu.next_button = ButtonC()
    menu.top_message = "Choose edition:"
    previous_choice = None
    try:
        with open('edition.conf') as f:
            previous_choice = editions.index(f.read().strip())
        menu.index = previous_choice
    except (OSError, ValueError):
        pass
    index = menu.run()
    if remember and index != previous_choice:
        with open('edition.conf', 'w') as f:
            f.write(editions[index])
            f.write("\n")
    return editions[index]
