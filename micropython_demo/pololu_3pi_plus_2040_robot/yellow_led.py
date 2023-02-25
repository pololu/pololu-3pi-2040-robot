from machine import Pin

class YellowLED:
    def __init__(self):
        self.pin = Pin(25, Pin.OUT)
        self.off()
    
    def on(self):
        self.pin.low()
        
    def off(self):
        self.pin.high()
    
    def value(self, value):
        self.pin.value(not value)
        
    def __call__(self, value):
        if value:
            self.on()
        else:
            self.off()
