from . import imu_sensor

_DEFAULT_ADDR = 0b1101011

_WHO_AM_I   = 0x0F
_CTRL1_XL   = 0x10
_CTRL2_G    = 0x11
_CTRL3_C    = 0x12
_STATUS_REG = 0x1E
_OUTX_L_G   = 0x22
_OUTX_L_XL  = 0x28

# encodings for CTRL1_XL.ODR_XL and CTRL2_G.ODR_G (high performance mode only)
_output_data_rate_encoding = {
    0:    0b0000,
    12.5: 0b0001,
    26:   0b0010,
    52:   0b0011,
    104:  0b0100,
    208:  0b0101,
    416:  0b0110,
    833:  0b0111,
    1666: 0b1000,
    3332: 0b1001,
    6664: 0b1010}

# encodings for CTRL1_XL.FS_XL
_acc_full_scale_encoding = {
    2:  0b00,
    4:  0b10,
    8:  0b11,
    16: 0b01}

# accelerometer sensitivity (LA_So) from mechanical characteristics table in
# mg/LSB
_acc_full_scale_to_sensitivity = {
    2:  0.061,
    4:  0.122,
    8:  0.244,
    16: 0.488}

# encodings for CTRL2_G.FS_G, FS_125
_gyro_full_scale_encoding = {
    125:  0b001,
    250:  0b000,
    500:  0b010,
    1000: 0b100,
    2000: 0b110}

# gyro sensitivity (G_So) from mechanical characteristics table in mdps/LSB
_gyro_full_scale_to_sensitivity = {
    125:  4.375,
    250:  8.75,
    500:  17.5,
    1000: 35,
    2000: 70}

class LSM6DSOAcc(imu_sensor.IMUSensor):
    def set_output_data_rate(self, hz):
        # note: this method doesn't support CTRL6_C.XL_HM_MODE = 1
        # (high-performance mode disabled)
        try:
            odr_xl = _output_data_rate_encoding[hz]
        except KeyError:
            raise ValueError(f"Invalid output data rate: {hz}")

        # CTRL1_XL.ODR_XL = odr_xl
        self._write_reg_masked(_CTRL1_XL, odr_xl << 4, 0xF0)

    def set_full_scale(self, g):
        # note: this method doesn't support CTRL8_XL.XL_FS_MODE = 1
        # (independent UI/OIS full scales bound to 8 g)
        try:
            fs_xl = _acc_full_scale_encoding[g]
            self._sensitivity = _acc_full_scale_to_sensitivity[g]
        except KeyError:
            raise ValueError(f"Invalid full scale: {g}")

        # CTRL1_XL.FS_XL = fs_xl
        self._write_reg_masked(_CTRL1_XL, fs_xl << 2, 0x0C)

    def enable_default(self):
        self.set_output_data_rate(52)
        self.set_full_scale(2)

    def data_ready(self):
        # STATUS_REG.XLDA
        return bool(self._read_reg(_STATUS_REG) & 0x01)

    def to_g(self, raw):
        return [x * self._sensitivity / 1000 for x in raw]

    def read(self):
        self.last_reading_raw = self._read_axes_s16(_OUTX_L_XL)
        self.last_reading_g = self.to_g(self.last_reading_raw)

class LSM6DSOGyro(imu_sensor.IMUSensor):
    def set_output_data_rate(self, hz):
        # note: this method doesn't support CTRL7_G.G_HM_MODE = 1
        # (high-performance mode disabled)
        try:
            odr_g = _output_data_rate_encoding[hz]
        except KeyError:
            raise ValueError(f"Invalid output data rate: {hz}")

        # CTRL2_G.ODR_G = odr_g
        self._write_reg_masked(_CTRL2_G, odr_g << 4, 0xF0)

    def set_full_scale(self, dps):
        try:
            fs_g_fs_125 = _gyro_full_scale_encoding[dps]
            self._sensitivity = _gyro_full_scale_to_sensitivity[dps]
        except KeyError:
            raise ValueError(f"Invalid full scale: {dps}")

        # CTRL2_G.FS_G, FS_125 = fs_g_fs_125
        self._write_reg_masked(_CTRL2_G, fs_g_fs_125 << 1, 0x0E)

    def enable_default(self):
        self.set_output_data_rate(208)
        self.set_full_scale(2000)

    def data_ready(self):
        # STATUS_REG.GDA
        return bool(self._read_reg(_STATUS_REG) & 0x02)

    def to_dps(self, raw):
        return [x * self._sensitivity / 1000 for x in raw]

    def read(self):
        self.last_reading_raw = self._read_axes_s16(_OUTX_L_G)
        self.last_reading_dps = self.to_dps(self.last_reading_raw)

class LSM6DSO(imu_sensor.IMUSensor):
    def __init__(self, i2c):
        self.acc = LSM6DSOAcc(i2c, _DEFAULT_ADDR)
        self.gyro = LSM6DSOGyro(i2c, _DEFAULT_ADDR)
        super().__init__(i2c, _DEFAULT_ADDR)

    @property
    def addr(self):
        return self._addr

    @addr.setter
    def addr(self, addr):
        self._addr = addr
        self.acc.addr = addr
        self.gyro.addr = addr

    def detect(self):
        return bool(self._read_reg(_WHO_AM_I) == 0x6C)

    def reset(self):
        # CTRL3_C.BOOT
        self._write_reg_masked(_CTRL3_C, 0x80, 0x80)
        while self._read_reg(_CTRL3_C) & 0x80: pass

        # CTRL3_C.SW_RESET
        self._write_reg_masked(_CTRL3_C, 0x01, 0x01)
        while self._read_reg(_CTRL3_C) & 0x01: pass

    def _config_default(self):
        # CTRL3_C.BDU = 1: block data update
        self._write_reg_masked(_CTRL3_C, 0x40, 0x40)

    def enable_default(self):
        self._config_default()
        self.acc.enable_default()
        self.gyro.enable_default()

    def read(self):
        self.acc.read()
        self.gyro.read()
