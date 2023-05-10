from machine import Pin, PWM, mem16, mem32
from micropython import const

MAX_SPEED = const(6000)
_PWM_BASE = const(0x40050000)
_CH7_DIV = const(_PWM_BASE + 0x90)
_CH7_CC = const(_PWM_BASE + 0x98)
_CH7_TOP = const(_PWM_BASE + 0x9c)

class Motors:
    def __init__(self):
        self.right_motor_dir = Pin(10, Pin.OUT, value=0)
        self.left_motor_dir = Pin(11, Pin.OUT, value=0)
        self.right_motor_pwm_pin = Pin(14, Pin.OUT, value=0)
        self.left_motor_pwm_pin = Pin(15, Pin.OUT, value=0)
        self.right_motor_pwm = PWM(self.right_motor_pwm_pin, freq=20833, duty_u16=0)
        self.left_motor_pwm = PWM(self.left_motor_pwm_pin, freq=20833, duty_u16=0)

        # Make sure there are 6000 different speeds, even if the
        # RP2040 is running at a non-standard frequency.
        mem32[_CH7_DIV] = 16             # do not divide clock
        mem32[_CH7_TOP] = MAX_SPEED - 1  # 6000 different speeds, 20833 Hz

        # You can edit these lines if your motors are reversed.
        self._flip_left_motor = False
        self._flip_right_motor = False
        
    def flip_left(self, flip):
        self._flip_left_motor = flip
        
    def flip_right(self, flip):
        self._flip_right_motor = flip
        
    def _set_dir_left(self, speed):
        speed = round(speed)
        if speed < 0:
            if speed < -MAX_SPEED: speed = -MAX_SPEED
            self.left_motor_dir.value(not self._flip_left_motor)
            return -speed
        elif speed > 0:
            if speed > MAX_SPEED: speed = MAX_SPEED
            self.left_motor_dir.value(self._flip_left_motor)
            return speed
        return 0
        
    def _set_dir_right(self, speed):
        speed = round(speed)
        if speed < 0:
            if speed < -MAX_SPEED: speed = -MAX_SPEED
            self.right_motor_dir.value(not self._flip_right_motor)
            return -speed
        elif speed > 0:
            if speed > MAX_SPEED: speed = MAX_SPEED
            self.right_motor_dir.value(self._flip_right_motor)
            return speed
        return 0
    
    def set_speeds(self, left, right):
        left = self._set_dir_left(left)
        right = self._set_dir_right(right)
        cc = (left << 16) | right
        mem32[_CH7_CC] = cc

    def set_left_speed(self, speed):
        speed = self._set_dir_left(speed)
        mem32[_CH7_CC] = (speed << 16) | (mem32[_CH7_CC] & 0xffff)
        
    def set_right_speed(self, speed):
        speed = self._set_dir_right(speed)
        mem32[_CH7_CC] = (mem32[_CH7_CC] & 0xffff0000) | speed

    def off(self):
        self.set_speeds(0, 0)

# For convenient access to this constant.
Motors.MAX_SPEED = MAX_SPEED
