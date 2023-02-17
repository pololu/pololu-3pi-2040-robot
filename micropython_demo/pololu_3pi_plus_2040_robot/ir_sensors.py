from machine import Pin
import array

_DONE = const(0)
_READ_LINE = const(1)
_READ_BUMP = const(2)

class IRSensors():
    def __init__(self):
        from ._lib.qtr_sensors import QTRSensors

        self.ir_down = Pin(26, Pin.IN)
        self.ir_bump = Pin(23, Pin.IN)
        self.qtr = QTRSensors(4, 16)
        
        self.reset_line_sensors_calibration()
        self.reset_bump_sensors_calibration()
        self._state = _DONE
    
    def reset_line_sensors_calibration(self):
        self.line_cal_min = array.array('H', [1024,1024,1024,1024,1024])
        self.line_cal_max = array.array('H', [0,0,0,0,0])
        
    def reset_bump_sensors_calibration(self):
        self.bump_cal_min = array.array('H', [1024,1024])
        self.bump_cal_max = array.array('H', [0,0])
        
    def calibrate_line_sensors(self):
        data = self.read_line_sensors()
        for i in range(5):
            self.line_cal_min[i] = min(data[i], self.line_cal_min[i])
        for i in range(5):
            self.line_cal_max[i] = max(data[i], self.line_cal_max[i])
            
    def calibrate_bump_sensors(self):
        data = self.read_bump_sensors()
        for i in range(2):
            self.bump_cal_min[i] = min(data[i], self.bump_cal_min[i])
        for i in range(2):
            self.bump_cal_max[i] = max(data[i], self.bump_cal_max[i])
    
    def start_read_line_sensors(self):
        self.ir_bump.init(Pin.IN)
        self.ir_down.init(Pin.OUT, value=1)
        self._state = _READ_LINE
        self.qtr.run()
        
    def start_read_bump_sensors(self):
        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.OUT, value=1)
        self._state = _READ_BUMP
        self.qtr.run()
    
    def read_line_sensors(self):
        if self._state != _READ_LINE:
            self.start_read_line_sensors()
        data = self.qtr.read()
        
        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.IN)
        self._state = _DONE
        return data[2:]
    
    def read_bump_sensors(self):
        if self._state != _READ_BUMP:
            self.start_read_bump_sensors()
        data = self.qtr.read()
        
        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.IN)
        self._state = _DONE
        return data[0:2]
    
    @micropython.viper
    def read_line_sensors_calibrated(self):
        data = self.read_line_sensors()
        d = ptr16(data)
        cal_min = ptr16(self.line_cal_min)
        cal_max = ptr16(self.line_cal_max)
        for i in range(5):
            if cal_min[i] >= cal_max[i] or d[i] < cal_min[i]:
                d[i] = 0
            elif d[i] > cal_max[i]:
                d[i]= 1000
            else:
               d[i] = (d[i] - cal_min[i])*1000 // (cal_max[i] - cal_min[i])
        return data
    
    @micropython.viper
    def read_bump_sensors_calibrated(self):
        data = self.read_bump_sensors()
        d = ptr16(data)
        cal_min = ptr16(self.bump_cal_min)
        cal_max = ptr16(self.bump_cal_max)
        for i in range(2):
            if 2 * d[i] > cal_min[i] + cal_max[i]:
                d[i] = 1000
            else:
                d[i] = 0
        return data
