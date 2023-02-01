from machine import Pin, PWM

class Motors:
    def __init__(self):
        self.right_motor_dir = Pin(10, Pin.OUT)
        self.left_motor_dir = Pin(11, Pin.OUT)
        self.right_motor_pwm_pin = Pin(14, Pin.OUT)
        self.left_motor_pwm_pin = Pin(15, Pin.OUT)
        self.right_motor_pwm = PWM(self.right_motor_pwm_pin)
        self.left_motor_pwm = PWM(self.left_motor_pwm_pin)
        self.left_motor_pwm.freq(20000)
    
    def set_speeds(self, left, right):
        if(left < 0):
            left = -left
            self.left_motor_dir.on()
        else:
            self.left_motor_dir.off()
        self.left_motor_pwm.duty_u16(left)
        
        if(right < 0):
            right = -right
            self.right_motor_dir.on()
        else:
            self.right_motor_dir.off()
        self.right_motor_pwm.duty_u16(right)
        
    def off(self):
        self.set_speeds(0, 0)