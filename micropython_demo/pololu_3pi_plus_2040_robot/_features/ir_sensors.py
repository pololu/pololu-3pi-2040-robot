from machine import Pin
from .._lib.qtr_sensors import *

class IRSensors():
    def __init__(self):
        self.ir_down = Pin(26, Pin.IN)
        self.ir_bump = Pin(23, Pin.IN)
        self.qtr = QTRSensors(4, 16)
        # TODO: actual calibration
        self.cal_min = array.array('H', [0,600,400,350,400,600,0])
        self.cal_max = array.array('H', [1024,1024,1024,1024,1024,1024,1024])
    
    def read_bump_sensors(self):
        self.ir_bump.init(Pin.OUT, value=1)
        self.qtr.run()
        sleep_us(1024)
        data = self.qtr.read()
        self.ir_bump.init(Pin.IN)
        return data[0:2]
    
    def run_line_sensors(self):
        self.ir_down.init(Pin.OUT, value=1)
        self.qtr.run()

    def read_line_sensors(self):
        self.data = self.qtr.read()[2:]
        self.ir_down.init(Pin.IN)
        return self.data
    
    def compute_line_calibrated(self):
        ret = array.array('H', [0,0,0,0,0])
        data = self.data
        for i in range(5):
            ret[i] = (min(max(data[i],self.cal_min[i+1]),self.cal_max[i+1]) - self.cal_min[i+1])*1000//(self.cal_max[i+1] - self.cal_min[i+1])
        return ret
