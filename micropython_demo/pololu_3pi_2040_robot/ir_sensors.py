from .buttons import Button
from machine import Pin
from array import array
import time
import rp2
from rp2 import PIO

TIMEOUT = const(1024)
_DONE = const(0)
_READ_LINE = const(1)
_READ_BUMP = const(2)
_state = _DONE
_qtr = None

class QTRSensors:
    """A 7-channel QTR sensor reader using PIO"""
    @rp2.asm_pio(
        out_init=(PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH),
        autopush=True, # saves push instructions
        push_thresh=23,
        fifo_join=PIO.JOIN_RX
        )
    def counter():
        # Set OSR to 32 bits of 1s for future shifting out to intialize pindirs,
        # y, y again, and x. This requires 7 + 8 + 10 + 7 = 32 bits.
        mov(osr, invert(null))

        # Set pindirs to 7 bits of 1s to enable output and start charging the capacitor.
        out(pindirs, 7)

        # Charge up the capacitors for ~32us.
        # Set Y counter to 255 by pulling another 8 bits from OSR.
        out(y, 8)
        label("charge")
        jmp(y_dec, "charge")

        # Load 1023 (10 bits of 1s) into Y as a counter
        out(y, 10)

        # Initialize X (last pin state) to 7 bits of 1s.
        out(x, 7)

        # Set pins back to inputs by writing 0s to pindirs.
        mov(osr, null)
        out(pindirs, 7)

        # loop is 8 instructions long = 1us
        label("loop")

        # read 7 pins into ISR
        in_(pins, 7)

        # save y in OSR
        mov(osr, y)

        # compare x to ISR
        mov(y, isr) # new value -> y
        jmp(x_not_y, "change")

        # discard the pin values and reset shift counter
        mov(isr, null)
        jmp("decrement")

        # a pin changed!
        label("change")
        mov(x, y) # save new pins

        # save and write data
        # 7 pins are in low bits of ISR
        in_(osr, 16) # time

        label("decrement")
        mov(y, osr) # restore y
        jmp(y_dec, "loop")

        # END OF PROGRAM
        label("finish")

        # Send 0xFFFFFFFF to tell the CPU we are done.
        in_(y, 32)

        wrap_target()
        nop()
        wrap()

    def __init__(self, id, pin1):
        Pin(pin1, Pin.IN, pull=None)
        Pin(pin1+1, Pin.IN, pull=None)
        Pin(pin1+2, Pin.IN, pull=None)
        Pin(pin1+3, Pin.IN, pull=None)
        Pin(pin1+4, Pin.IN, pull=None)
        Pin(pin1+5, Pin.IN, pull=None)
        Pin(pin1+6, Pin.IN, pull=None)
        p = Pin(pin1, Pin.OUT, value=1)
        Pin(pin1+1, Pin.OUT, value=1)
        Pin(pin1+2, Pin.OUT, value=1)
        Pin(pin1+3, Pin.OUT, value=1)
        Pin(pin1+4, Pin.OUT, value=1)
        Pin(pin1+5, Pin.OUT, value=1)
        Pin(pin1+6, Pin.OUT, value=1)

        self.sm = rp2.StateMachine(id, self.counter, freq=8000000, in_base=p, out_base=p)
        self.data_bump = array('H', [0,0])
        self.data_line = array('H', [0,0,0,0,0])

    def run(self):
        while self.sm.rx_fifo():
            self.sm.get()
        self.sm.restart()
        self.sm.active(1)

    @micropython.viper
    def read_bump(self):
        last_states = uint(0x7f0000)
        data = ptr16(self.data_bump)
        data[0] = TIMEOUT
        data[1] = TIMEOUT

        sm = self.sm
        while True:  # TODO: TIMEOUT?
            val = uint(sm.get())
            if(val == uint(0xffffffff)):
                break
            new_zeros = last_states ^ val
            if new_zeros & 0x10000:
                data[1] = TIMEOUT - val
            if new_zeros & 0x20000:
                data[0] = TIMEOUT - val
            last_states = val
        return self.data_bump

    @micropython.viper
    def read_line(self):
        last_states = uint(0x7f0000)
        data = ptr16(self.data_line)
        for i in range(5):
            data[i] = TIMEOUT

        sm = self.sm
        while True:  # TODO: TIMEOUT?
            val = uint(sm.get())
            if(val == uint(0xffffffff)):
                break
            new_zeros = last_states ^ val
            if new_zeros & 0x40000:
                data[4] = TIMEOUT - val
            if new_zeros & 0x80000:
                data[3] = TIMEOUT - val
            if new_zeros & 0x100000:
                data[2] = TIMEOUT - val
            if new_zeros & 0x200000:
                data[1] = TIMEOUT - val
            if new_zeros & 0x400000:
                data[0] = TIMEOUT - val
            last_states = val
        return self.data_line

class _IRSensors():
    def __init__(self):
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
        return _state

    def reset_calibration(self):
        self.cal_min = array('H', [1025, 1025, 1025, 1025, 1025])
        self.cal_max = array('H', [0, 0, 0, 0, 0])

    def calibrate(self):
        tmp_min = array('H', [1025, 1025, 1025, 1025, 1025])
        tmp_max = array('H', [0, 0, 0, 0, 0])

        # do 10 measurements
        for trials in range(10):
            data = self.read()
            for i in range(5):
                tmp_min[i] = min(data[i], tmp_min[i])
                tmp_max[i] = max(data[i], tmp_max[i])

        # update data only if ALL data beyond one of the limits
        for i in range(5):
            self.cal_max[i] = max(tmp_min[i], self.cal_max[i])
            self.cal_min[i] = min(tmp_max[i], self.cal_min[i])

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

class BumpButton(Button):
    def __init__(self, read_func, is_pressed_func):
        self._read_func = read_func
        self._is_pressed_func = is_pressed_func
        super().__init__()

    def read(self): return self._read_func()
    def is_pressed(self): return self._is_pressed_func()

class BumpSensors(_IRSensors):
    def __init__(self):
        self._left_is_pressed = False
        self._right_is_pressed = False
        self._last_left_is_pressed = False
        self._last_right_is_pressed = False
        self.left = BumpButton(self.read, self.left_is_pressed)
        self.right = BumpButton(self.read, self.right_is_pressed)
        super().__init__()

    def _state(self):
        # for testing
        return _state

    def reset_calibration(self):
        # start at 1025 so it will not register a bump without calibration,
        # and we can easily tell it's not calibrated.
        self.threshold_min = array('H', [1025, 1025])
        self.threshold_max = array('H', [1025, 1025])

    def calibrate(self, count=50):
        sum = [0, 0]
        for i in range(count):
            data = self.read()
            sum[0] += data[0]
            sum[1] += data[1]

        # Set the thresholds to 140% and 160% of the average reading.
        for i in range(2):
            self.threshold_min[i] = round(sum[i] * 1.4 / count)
            self.threshold_max[i] = round(sum[i] * 1.6 / count)

    def start_read(self):
        global _state
        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.OUT, value=1)

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

        self._left_is_pressed = data[0] > \
          (self.threshold_min[0] if self._left_is_pressed else self.threshold_max[0])

        self._right_is_pressed = data[1] > \
          (self.threshold_min[1] if self._right_is_pressed else self.threshold_max[1])

        return data

    def left_is_pressed(self):
        return self._left_is_pressed

    def right_is_pressed(self):
        return self._right_is_pressed

    def left_changed(self):
        return self._left_is_pressed != self._last_left_is_pressed

    def right_changed(self):
        return self._right_is_pressed != self._last_right_is_pressed
