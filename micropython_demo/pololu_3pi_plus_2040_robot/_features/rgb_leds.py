from machine import Pin, SPI

class RGBLEDs():
    def __init__(self):
        self.sck_pin = Pin(6)
        self.spi = SPI(id=0, baudrate=4000000, polarity=0, phase=0, sck=self.sck_pin, mosi=Pin(3), miso=Pin(0))
        
        # fix the mode of Pin 0
        Pin(0).init(Pin.OUT, value=0)
        
        self.brightness = [15,15,15,15,15,15] # max brightness
        self.off()

    def show(self):
        list=[]
        # start frame: 4 zeros
        list.append(0)
        list.append(0)
        list.append(0)
        list.append(0)
        
        # data frames
        i = 0
        for rgb in self.values:
            list.append(0xe0 + self.brightness[i])
            list.append(rgb[2])
            list.append(rgb[1])
            list.append(rgb[0])
            i = i + 1
        
        # end frame
        list.append(0xff)
        list.append(0xff)
        list.append(0xff)
        list.append(0xff)
        # note: maybe need extra end bytes?
        
        self.sck_pin.init(mode=Pin.ALT, alt=1)
        self.spi.write(bytearray(list))
        self.sck_pin(0)
        self.sck_pin.init(mode=Pin.OUT)

    def set_brightness(self, led, value):
        self.brightness[led] = value

    def set(self, led, rgb):
        self.values[led] = rgb
        
    def off(self):
        self.values = [[0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0]]
        self.show()

