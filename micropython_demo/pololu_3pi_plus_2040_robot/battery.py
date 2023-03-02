class Battery:
    def __init__(self):
        from machine import Pin, ADC
        self.adc = ADC(Pin(26))

    def get_level_millivolts(self):
        sum = 0
        for i in range(10):
            sum += self.adc.read_u16()
        avg = sum / 10
        return int(3300 * avg * 11 / 65536)
