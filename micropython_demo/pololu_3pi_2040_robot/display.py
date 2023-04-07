from ._lib import sh1106_shared_spi
from machine import Pin, SPI
import framebuf

class Display(sh1106_shared_spi.SH1106SharedSpi):
    def __init__(self):
        sck_pin = Pin(2)
        spi = SPI(id=0, baudrate=4000000, polarity=0, phase=0, sck=sck_pin, mosi=Pin(3), miso=None)
        dc = Pin(0)   # data/command
        res = Pin(1)  # reset
        super().__init__(128, 64, spi, dc, sck_pin, res=res, rotate=180)

    def load_pbm(self, filename):
        f = open(filename, 'rb')
        f.readline() # Magic number
        f.readline() # Creator comment
        f.readline() # Dimensions
        data = bytearray(f.read())
        return framebuf.FrameBuffer(data, 128, 64, framebuf.MONO_HLSB)
