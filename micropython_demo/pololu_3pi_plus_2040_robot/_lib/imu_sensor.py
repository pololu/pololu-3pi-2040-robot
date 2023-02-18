import struct

class IMUSensor:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr

    def _read_reg(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _write_reg(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))

    def _write_reg_masked(self, reg, val, mask):
        self._write_reg(reg, (self._read_reg(reg) & ~mask) | (val & mask))

    def _read_axes_s16(self, first_reg):
        buf = self.i2c.readfrom_mem(self.addr, first_reg, 6)
        return list(struct.unpack('<3h', buf))