from machine import Pin

_DONE = const(0)
_READ_LINE = const(1)
_READ_BUMP = const(2)

class IRSensors():
    def __init__(self):
        from ._lib.qtr_sensors import QTRSensors
        import array

        self.ir_down = Pin(26, Pin.IN)
        self.ir_bump = Pin(23, Pin.IN)
        self.qtr = QTRSensors(4, 16)
        # TODO: actual calibration
        self.cal_min = array.array('H', [0,600,400,350,400,600,0])
        self.cal_max = array.array('H', [1024,1024,1024,1024,1024,1024,1024])
        self._state = _DONE
   
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
    
    def compute_line_calibrated(self):
        ret = array.array('H', [0,0,0,0,0])
        data = self.data
        for i in range(5):
            ret[i] = (min(max(data[i],self.cal_min[i+1]),self.cal_max[i+1]) - self.cal_min[i+1])*1000//(self.cal_max[i+1] - self.cal_min[i+1])
        return ret
