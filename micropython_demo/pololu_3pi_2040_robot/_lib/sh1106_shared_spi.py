from . import sh1106
from machine import Pin
from micropython import const

# Wrapper for SH1106 that is safe to use with multiple SPI buses
# sharing all pins except SCK.
#
# At the end of every method call this library dissociates the SCK
# pin from the bus, and at the beginning of each call it associates
# it again.
#
# Also includes an optimized version of the show() method.

# a few register definitions
_SET_DISP            = const(0xae)
_LOW_COLUMN_ADDRESS  = const(0x00)
_HIGH_COLUMN_ADDRESS = const(0x10)
_SET_PAGE_ADDRESS    = const(0xB0)


class SH1106SharedSpi(sh1106.SH1106_SPI):
    
    def __init__(self, width, height, spi, dc, sck, res=None, cs=None,
                 rotate=0, external_vcc=False):
    
        self.sck = sck
        
        # This first switch can cause a glitch, so do it before resetting.
        # See https://github.com/micropython/micropython/issues/10226
        self.sck.init(mode=Pin.OUT, value=0)
        
        self.sck.init(mode=Pin.ALT, alt=1)
        super().__init__(width, height, spi, dc, res=res, cs=cs,
                         rotate=rotate, external_vcc=external_vcc)

    def show(self, full_update = False):
        # self.* lookups in loops take significant time (~4fps).
        (w, p, db, rb) = (self.width, self.pages,
                          self.displaybuf, self.renderbuf)
        s = self.spi
        dc = self.dc

        if self.rotate90:
            for i in range(self.bufsize):
                db[w * (i % p) + (i // p)] = rb[i]
        if full_update:
            pages_to_update = (1 << self.pages) - 1
        else:
            pages_to_update = self.pages_to_update
        
        self.sck.init(mode=Pin.ALT, alt=1)
        
        # set column low bits once
        self.dc(0)
        cmd = bytearray(3)
        cmd[0] = _LOW_COLUMN_ADDRESS | 2
        cmd[1] = _HIGH_COLUMN_ADDRESS
        
        for page in range(self.pages):
            if (pages_to_update & (1 << page)):
                # set the start position, inline
                dc(0)
                cmd[2] = _SET_PAGE_ADDRESS | page
                s.write(cmd)
                
                # write the data, inline
                dc(1)
                s.write(db[page*w:page*w+w])
        
        self.sck.init(mode=Pin.OUT, value=0)
        
        self.pages_to_update = 0
        
    # override unnecessarily slow poweron command in the SH1106 library
    def poweron(self):
        self.write_cmd(_SET_DISP | 0x01)

    def write_cmd(self, cmd):
        self.sck.init(mode=Pin.ALT, alt=1)
        self.dc(0)
        self.spi.write(bytearray([cmd]))
        self.sck.init(mode=Pin.OUT, value=0)