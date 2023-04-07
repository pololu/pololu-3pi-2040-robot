# Functions for selecting what edition of the 3pi+ 2040 is being used:
# standard, turtle, or hyper.

from pololu_3pi_2040_robot.extras.menu import Menu
from pololu_3pi_2040_robot.display import Display
from pololu_3pi_2040_robot.buttons import ButtonA, ButtonB, ButtonC
from pololu_3pi_2040_robot.buzzer import Buzzer

editions = [ "Standard", "Turtle", "Hyper" ]

def select(*, remember=True):
    menu = Menu(editions)
    menu.display = Display()
    menu.buzzer = Buzzer()
    menu.previous_button = ButtonA()
    menu.select_button = ButtonB()
    menu.next_button = ButtonC()
    menu.top_message = 'Choose edition:'
    try:
        with f = open("edition.conf"):
            previous_choice = f.read()
        menu.index = editions.index(previous_choice)
    except OSError:
        pass
    index = menu.run()
    if remember:
      # TODO: write to edition.conf
      pass
    return editions[index]
