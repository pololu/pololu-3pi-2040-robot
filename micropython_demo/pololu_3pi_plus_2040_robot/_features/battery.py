from machine import Pin, ADC

class Battery:
    def __init__(self):
        self.adc = ADC(Pin(26))

    def get_level_millivolts(self):
        return int(3300 * self.adc.read_u16() * 11 / 65536)