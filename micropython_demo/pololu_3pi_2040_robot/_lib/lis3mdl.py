from . import imu_sensor

_DEFAULT_ADDR = 0b0011110

_WHO_AM_I   = 0x0F
_CTRL_REG1  = 0x20
_CTRL_REG2  = 0x21
_CTRL_REG3  = 0x22
_CTRL_REG4  = 0x23
_CTRL_REG5  = 0x24
_STATUS_REG = 0x27
_OUT_X_L    = 0x28

# encodings for CTRL_REG1.DO
_output_data_rate_encoding = {
    0.625: 0b000,
    1.25:  0b001,
    2.5:   0b010,
    5:     0b011,
    10:    0b100,
    20:    0b101,
    40:    0b110,
    80:    0b111}

# encodings for CTRL_REG2.FS
_full_scale_encoding = {
    4:  0b00,
    8:  0b01,
    12: 0b10,
    16: 0b11}

# sensitivity (GN) from magnetic characteristics table in LSB/gauss
_full_scale_to_sensitivity = {
    4:  6842,
    8:  3421,
    12: 2281,
    16: 1711}

class LIS3MDL(imu_sensor.IMUSensor):
    def __init__(self, i2c):
        super().__init__(i2c, _DEFAULT_ADDR)

    def detect(self):
        return bool(self._read_reg(_WHO_AM_I) == 0x3D)

    def reset(self):
        # CTRL_REG2.REBOOT
        self._write_reg_masked(_CTRL_REG2, 0x08, 0x08)
        while self._read_reg(_CTRL_REG2) & 0x08: pass

        # CTRL_REG2.SOFT_RST
        self._write_reg_masked(_CTRL_REG2, 0x04, 0x04)
        while self._read_reg(_CTRL_REG2) & 0x04: pass

    def _config_default(self):
        # CTRL_REG3.MD = 00: continuous-conversion mode
        self._write_reg_masked(_CTRL_REG3, 0x00, 0x03)

        # CTRL_REG5.BDU = 1: block data update
        self._write_reg_masked(_CTRL_REG5, 0x40, 0x40)

        # CTRL_REG1.OM = 11: XY-axis ultra-high-performance mode
        self._write_reg_masked(_CTRL_REG1, 0x60, 0x60)

        # CTRL_REG4.OMZ = 11: Z-axis ultra-high-performance mode
        self._write_reg_masked(_CTRL_REG4, 0x0C, 0x0C)

    def set_output_data_rate(self, hz):
        # note: this method doesn't support CTRL_REG1.FAST_ODR = 1 (ODR > 80 Hz)
        try:
            do = _output_data_rate_encoding[hz]
        except KeyError:
            raise ValueError(f"Invalid output data rate: {hz}")

        # CTRL_REG1.DO = do
        self._write_reg_masked(_CTRL_REG1, do << 2, 0x1C)

    def set_full_scale(self, gauss):
        try:
            fs = _full_scale_encoding[gauss]
            self._sensitivity = _full_scale_to_sensitivity[gauss]
        except KeyError:
            raise ValueError(f"Invalid full scale: {gauss}")

        # CTRL_REG2.FS = fs
        self._write_reg_masked(_CTRL_REG2, fs << 5, 0x60)

    def enable_default(self):
        self._config_default()
        self.set_output_data_rate(10)
        self.set_full_scale(4)

    def data_ready(self):
        # STATUS_REG.ZYXDA
        return bool(self._read_reg(_STATUS_REG) & 0x80)

    def to_gauss(self, raw):
        return [x / self._sensitivity for x in raw]

    def read(self):
        self.last_reading_raw = self._read_axes_s16(_OUT_X_L)
        self.last_reading_gauss = self.to_gauss(self.last_reading_raw)
