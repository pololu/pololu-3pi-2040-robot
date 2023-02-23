from machine import Pin
from array import array
import time

_DONE = const(0)
_READ_LINE = const(1)
_READ_BUMP = const(2)
_state = _DONE
_qtr = None

class _IRSensors():
    def __init__(self):
        from ._lib.qtr_sensors import QTRSensors

        self.ir_down = Pin(26, Pin.IN)
        self.ir_bump = Pin(23, Pin.IN)

        global _qtr
        if not _qtr:
            _qtr = QTRSensors(4, 16)
        self.qtr = _qtr

        self.reset_calibration()

class LineSensors(_IRSensors):
    def _state(self):
        # for testing
        global _state
        return _state

    def reset_calibration(self):
        self.cal_min = array('H', [1024,1024,1024,1024,1024])
        self.cal_max = array('H', [0,0,0,0,0])

    def calibrate(self):
        data = self.read()
        for i in range(5):
            self.cal_min[i] = min(data[i], self.cal_min[i])
        for i in range(5):
            self.cal_max[i] = max(data[i], self.cal_max[i])

    def start_read(self):
        global _state
        self.ir_bump.init(Pin.IN)
        self.ir_down.init(Pin.OUT, value=1)
        _state = _READ_LINE
        self.qtr.run()

    @micropython.viper
    def read(self):
        global _state
        if uint(_state) != uint(_READ_LINE):
            self.start_read()
        data = self.qtr.read_line()

        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.IN)
        _state = _DONE
        return data
        #return array('H', [data[6], data[5], data[4], data[3], data[2]])

    @micropython.viper
    def read_calibrated(self):
        data = self.read()
        d = ptr16(data)
        cal_min = ptr16(self.cal_min)
        cal_max = ptr16(self.cal_max)
        for i in range(5):
            if cal_min[i] >= cal_max[i] or d[i] < cal_min[i]:
                d[i] = 0
            elif d[i] > cal_max[i]:
                d[i]= 1000
            else:
               d[i] = (d[i] - cal_min[i])*1000 // (cal_max[i] - cal_min[i])
        return data

class BumpSensors(_IRSensors):
    def __init__(self):
        self.margin_percentage = 50
        self._left_is_pressed = False
        self._right_is_pressed = False
        self._last_left_is_pressed = False
        self._last_right_is_pressed = False
        super().__init__()

    def _state(self):
        # for testing
        global _state
        return _state

    def reset_calibration(self):
        self.cal = array('H', [200, 200])

    def calibrate(self, count=50):
        cal = [0, 0]
        for i in range(count):
            data = self.read()
            cal[0] += data[0]
            cal[1] += data[1]
        self.cal[0] = cal[0] // count
        self.cal[1] = cal[1] // count

    def start_read(self):
        global _state
        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.OUT, value=1)

        # Bump sensors seem to be slower than
        # the line sensors and need about 200us
        # of illumination to reach consistent
        # levels.
        time.sleep_us(200)

        _state = _READ_BUMP
        self.qtr.run()

    @micropython.viper
    def read(self):
        global _state
        if uint(_state) != uint(_READ_BUMP):
            self.start_read()
        data = self.qtr.read_bump()

        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.IN)
        _state = _DONE

        self._last_left_is_pressed = self._left_is_pressed
        self._last_right_is_pressed = self._right_is_pressed
        self._left_is_pressed = uint(data[0])*100 > uint(self.cal[0])*(100 + uint(self.margin_percentage))
        self._right_is_pressed = uint(data[1])*100 > uint(self.cal[1])*(100 + uint(self.margin_percentage))
        return data

    def left_is_pressed(self):
        return self._left_is_pressed

    def right_is_pressed(self):
        return self._right_is_pressed

    def left_changed(self):
        return self._left_is_pressed != self._last_left_is_pressed

    def right_changed(self):
        return self._right_is_pressed != self._last_right_is_pressed
