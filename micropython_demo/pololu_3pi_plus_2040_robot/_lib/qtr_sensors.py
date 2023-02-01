from machine import Pin
import rp2
from rp2 import PIO
import array
from time import *
    
class QTRSensors:
    """A 7-channel QTR sensor reader using PIO"""
        
    @rp2.asm_pio(
        out_init=(PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH,PIO.OUT_HIGH),
        autopush=True, # saves push instructions
        fifo_join=PIO.JOIN_RX
        )
    def counter():
        # set pins to inputs
        mov(osr, null)
        out(pindirs, 7)
        
        # load 1023 (10 bits of 1s) into y as a counter
        mov(osr, invert(null))
        out(y, 10)
        
        # loop is ~8 instructions long = 1us
        label("loop")
        
        # reset shift counter and read 7 pins into ISR
        mov(isr, null)
        in_(pins, 7)
        
        # save y in OSR
        mov(osr, y)
        
        # compare x to ISR
        mov(y, isr) # new value -> y
        jmp(x_not_y, "change")
        
        # done checking
        jmp("decrement")

        # a pin changed!
        label("change")    
        mov(x, y) # save new pins
        
        # save and write data (why didn't we have to reset the shift counter?)
        in_(osr, 16) # time
        in_(x, 16) # value
        
        label("decrement")
        mov(y, osr) # restore y
        jmp(y_dec, "loop")
        
        # END OF PROGRAM
        label("finish")
        
        # Set pins back to outputs
        mov(osr, invert(null))
        out(pindirs, 7)
        
        label("done")
        jmp("done")
    
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
        self.data[0] = 0
        self.data[1] = 0
        self.data[2] = 0
        self.data[3] = 0
        self.data[4] = 0
        self.data[5] = 0
        self.data[6] = 0
        
        while self.sm.rx_fifo():
            self.sm.get()
        self.sm.restart()
        self.sm.active(1)
        
    def read(self):
        last_states = 0x7f
        while(self.sm.rx_fifo()):
            data = self.sm.get()
            if(data == 0xffffffff):
                break
            time = data >> 16
            states = data & 0x7f
            new_zeros = last_states & ~states
            if new_zeros & 1:
                self.data[0] = time
            if new_zeros & 2:
                self.data[1] = time
            if new_zeros & 4:
                self.data[2] = time
            if new_zeros & 8:
                self.data[3] = time
            if new_zeros & 16:
                self.data[4] = time
            if new_zeros & 32:
                self.data[5] = time
            if new_zeros & 64:
                self.data[6] = time
            last_states = states
        
        return self.data

