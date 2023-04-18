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
        with open(filename, 'rb') as f:
            f.readline() # Magic number
            f.readline() # Creator comment
            f.readline() # Dimensions
            data = bytearray(f.read())
        return framebuf.FrameBuffer(data, 128, 64, framebuf.MONO_HLSB)

    def save_pbm(self, filename):
        buf = bytearray(self.bufsize)
        data = framebuf.FrameBuffer(buf, self.width, self.height, framebuf.MONO_HLSB)
        data.blit(self, 0, 0)
        with open(filename, 'wb') as f:
            f.write("P4\n128 64\n")
            f.write(data)

    def exception(self, e):
        self.text(type(e).__name__ + ":", 0, 0, 1)
        try:
            # Try to use https://github.com/micropython/micropython/pull/11244
            from sys import _exc_traceback
            tb = _exc_traceback(e)
            line_numbers = []
            i = len(tb) - 3
            while i >= 0:
                line_numbers.append(tb[i + 1])
                if tb[i + 2] == 'run_file': line_numbers.clear()
                i -= 3
            tb_line = ",".join(map(str, line_numbers))
            if len(tb_line) <= 11: tb_line = "Line " + tb_line
            self.text(tb_line, 0, 56, 1)
            msg_line_count = 6
        except ImportError:
            msg_line_count = 7
        msg = str(e)
        for i in range(msg_line_count):
            msg_line = msg[i*16:(i+1)*16]
            self.text(msg_line, 0, 8 * (i + 1), 1)

    def show_exception(e):
        display = Display()
        display.exception(e)
        display.show()
