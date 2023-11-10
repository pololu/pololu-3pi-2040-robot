import array
import struct

class IMUSensor:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        self._buf = array.array('h', [0, 0, 0])

    def _read_reg(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _write_reg(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))

    def _write_reg_masked(self, reg, val, mask):
        self._write_reg(reg, (self._read_reg(reg) & ~mask) | (val & mask))

    def _read_axes_s16(self, first_reg):
        self.i2c.readfrom_mem_into(self.addr, first_reg, self._buf)
        return list(struct.unpack('<3h', self._buf))