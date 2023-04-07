from machine import Pin, SPI
from micropython import const

class RGBLEDs():
    def __init__(self, led_count = 6):
        self.sck_pin = Pin(6)
        self.spi = SPI(id=0, baudrate=20000000, polarity=0, phase=0,
                       sck=self.sck_pin, mosi=Pin(3), miso=Pin(0))

        # fix the mode of Pin 0
        Pin(0).init(Pin.OUT, value=0)

        # initialize the data array
        self._led_count = led_count
        self.data = bytearray(
            4 +
            led_count*4 +
            (led_count + 14) // 16
            )
        self.set_brightness(31)

        self.off()

    def show(self):
        self.sck_pin.init(mode=Pin.ALT, alt=1)
        self.spi.write(self.data)
        self.sck_pin(0)
        self.sck_pin.init(mode=Pin.OUT)

    def set_brightness(self, value, led=None):
        if led != None:
            self.data[4 + led*4] = 0xe0 | (round(value) & 0x1f)
        else:
            for l in range(self._led_count):
                self.set_brightness(value, led=l)
    
    def get_brightness(self, led=0):
        return self.data[4 + led*4] & 0x1f

    def set(self, led, rgb):
        self.data[4 + led*4 + 1] = round(rgb[2])
        self.data[4 + led*4 + 2] = round(rgb[1])
        self.data[4 + led*4 + 3] = round(rgb[0])

    def get(self, led):
        return [
            self.data[4 + led*4 + 3],
            self.data[4 + led*4 + 2],
            self.data[4 + led*4 + 1]
            ]
    
    def set_hsv(self, led, hsv, h_scale=360):
        self.set(led, self.hsv2rgb(hsv[0], hsv[1], hsv[2], h_scale=h_scale))

    def hsv2rgb(self, h, s, v, h_scale=360):
        # adapted from https://stackoverflow.com/a/14733008
        # but with variable hue scale
        sixth = (h_scale + 3) // 6
        if s == 0:
            return [v, v, v]

        h = h % h_scale
        region = h // sixth
        remainder = (h - (region * sixth)) * 6
        p = (v * (255 - s)) // 255
        q = (v * (255 - ((s * remainder) // h_scale))) // 255
        t = (v * (255 - ((s * (h_scale - remainder)) // h_scale))) // 255

        if region == 0:
            return [v, t, p]
        elif region == 1:
            return [q, v, p]
        elif region == 2:
            return [p, v, t]
        elif region == 3:
            return [p, q, v]
        elif region == 4:
            return [t, p, v]
        else:
            return [v, p, q]
        
    def off(self):
        for led in range(self._led_count):
            self.set(led, [0, 0, 0])
        self.show()
