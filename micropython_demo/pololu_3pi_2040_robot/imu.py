class IMU:
    def __init__(self, i2c=None):
        from ._lib import lis3mdl, lsm6dso
        if i2c is None:
            from machine import I2C, Pin
            i2c = I2C(id=0, scl=Pin(5), sda=Pin(4), freq=400_000)
            # Send low pulses on SCL to fix devices that are stuck
            # driving SDA low.
            for i in range(10):
                try: i2c.writeto(0, "")
                except OSError: pass
        self._lsm6dso = lsm6dso.LSM6DSO(i2c)
        self._lis3mdl = lis3mdl.LIS3MDL(i2c)
        self.gyro = self._lsm6dso.gyro
        self.acc = self._lsm6dso.acc
        self.mag = self._lis3mdl

    def detect(self):
        return self._lsm6dso.detect() and self._lis3mdl.detect()

    def reset(self):
        self._lsm6dso.reset()
        self._lis3mdl.reset()

    def enable_default(self):
        self._lsm6dso.enable_default()
        self._lis3mdl.enable_default()

    def read(self):
        self.gyro.read()
        self.acc.read()
        self.mag.read()
