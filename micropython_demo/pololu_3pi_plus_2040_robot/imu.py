from ._lib import lis3mdl, lsm6dso
from machine import I2C, Pin

class IMU:
    def __init__(self):
        i2c = I2C(id=0, scl=Pin(5), sda=Pin(4), freq=400_000)
        self._lsm6 = lsm6dso.LSM6DSO(i2c)
        self.gyro = self._lsm6.gyro
        self.acc = self._lsm6.acc
        self.mag = lis3mdl.LIS3MDL(i2c)

    def reset(self):
        self._lsm6.reset()
        self.mag.reset()

    def enable_default(self):
        self._lsm6.enable_default()
        self.mag.enable_default()