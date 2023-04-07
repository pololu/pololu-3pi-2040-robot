class Menu:
    def __init__(self, options):
        self.top_message = "Select:"
        self.options = options
        self.display = None
        self.buzzer = None
        self.previous_button = None
        self.next_button = None
        self.select_button = None
        self.previous_button_beep = "!c32"
        self.select_button_beep = "!e32"
        self.next_button_beep = "!g32"
        self.index = 0
        self.first_update = True

    def update(self):
        if self.first_update:
            # Consume any immediate button events from a button being
            # pressed already when the menu is opened.
            if self.previous_button:
                self.previous_button.check()
            if self.select_button:
                self.select_button.check()
            if self.next_button:
                self.next_button.check()
            self.first_update = False

        count = len(self.options)

        if self.display:
            self.display.fill(0)

            y = 18
            self.display.fill_rect(0, y-1, 127, 10, 1)
            for i in range(count):
                if self.index == i:
                    self.display.text(self.options[i], 0, y - self.index*10, 0)
                else:
                    self.display.text(self.options[i], 0, y - self.index*10)

                y += 10

            self.display.fill_rect(0, 0, 127, 10, 0)
            self.display.line(0, 10, 127, 10, 1)
            self.display.text(self.top_message, 0, 0)

            self.display.show()
        if self.next_button and self.next_button.check():
            if self.buzzer and self.next_button_beep:
                self.buzzer.play_in_background(self.next_button_beep)
            self.index = (self.index + 1) % count
        if self.previous_button and self.previous_button.check():
            if self.buzzer and self.previous_button_beep:
                self.buzzer.play_in_background(self.previous_button_beep)
            self.index = (self.index - 1) % count
        if self.select_button and self.select_button.check():
            if self.buzzer and self.select_button_beep:
                self.buzzer.play_in_background(self.select_button_beep)
            return self.index

    def run(self):
        self.first_update = True
        while self.update() is None: pass
        return self.index
