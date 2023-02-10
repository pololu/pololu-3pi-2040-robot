from machine import Pin
import rp2
from rp2 import PIO
import array
from time import *
from micropython import const

TIMEOUT = const(1024)

class QTRSensors:
    """A 7-channel QTR sensor reader using PIO"""    
    @rp2.asm_pio(
        out_init=(PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH),
        autopush=True, # saves push instructions
        push_thresh=23,
        fifo_join=PIO.JOIN_RX
        )
    def counter():
        # set pins to inputs
        mov(osr, null) # sm.restart() does not clear OSR
        out(pindirs, 7)
        
        # load 1023 (10 bits of 1s) into y as a counter
        mov(osr, invert(null))
        out(y, 10)
        
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
        
        # Set pins back to outputs
        mov(osr, invert(null))
        out(pindirs, 7)
        
        # Send 0xFFFFFFFF to tell the CPU we are done.
        in_(y, 32)
        
        wrap_target()
    
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
        self.data = array.array('H', [0,0,0,0,0,0,0])
        self.run()
        
    def run(self):
        for i in range(7):
            self.data[i] = TIMEOUT
        
        while self.sm.rx_fifo():
            self.sm.get()
        self.sm.restart()
        self.sm.active(1)

    @micropython.viper
    def read(self):
        last_states = uint(0x7f0000)
        data = ptr16(self.data)
        sm = self.sm
        while(True): # TODO: TIMEOUT?
            val = uint(sm.get())
            if(val == uint(0xffffffff)):
                break
            new_zeros = last_states ^ val
            if new_zeros & 0x10000:
                data[0] = TIMEOUT - val
            if new_zeros & 0x20000:
                data[1] = TIMEOUT - val
            if new_zeros & 0x40000:
                data[2] = TIMEOUT - val
            if new_zeros & 0x80000:
                data[3] = TIMEOUT - val
            if new_zeros & 0x100000:
                data[4] = TIMEOUT - val
            if new_zeros & 0x200000:
                data[5] = TIMEOUT - val
            if new_zeros & 0x400000:
                data[6] = TIMEOUT - val
            last_states = val
        
        return self.data

