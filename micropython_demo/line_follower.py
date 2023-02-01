import time
import random
import rp2
from machine import Pin
import pololu_3pi_plus_2040_robot as robot
import _thread
from array import *

button_a = robot.ButtonA()
button_b = robot.ButtonB()
button_c = robot.ButtonC()

rgb_leds = robot.RGBLEDs()
display = robot.Display()
led = robot.YellowLED()
motors = robot.Motors()
encoders = robot.Encoders()
buzzer = robot.Buzzer()
battery = robot.Battery()
ir_sensors = robot.IRSensors()
t1 = 0
t2 = time.ticks_us()
p = 0
line = []

def updateDisplay():
    global display
    global ir_sensors
    global t1, t2
    global c
    global p
    global line
    
    display.fill(0)
    display.text("Line Follower", 0, 0)
    display.text("Main loop: "+str((t2-t1)//1000)+'.'+str((t2-t1)//100%10)+ 'ms', 0, 20)
    display.text('p = '+str(p), 0, 30)
    
    # 64-40 = 24
    scale = 24/1023
    #display.rect(0, 64-int(bump[1]*scale), 8, int(bump[1]*scale), 1)  
    
    display.fill_rect(36, 64-int((1000-line[4])*scale), 8, int((1000-line[4])*scale), 1)
    display.fill_rect(48, 64-int((1000-line[3])*scale), 8, int((1000-line[3])*scale), 1)
    display.fill_rect(60, 64-int((1000-line[2])*scale), 8, int((1000-line[2])*scale), 1)
    display.fill_rect(72, 64-int((1000-line[1])*scale), 8, int((1000-line[1])*scale), 1)
    display.fill_rect(84, 64-int((1000-line[0])*scale), 8, int((1000-line[0])*scale), 1)
    
    #display.rect(120, 64-int(bump[0]*scale), 8, int(bump[0]*scale), 1)
    display.show()
    
    display.show()

if button_a.isPressed():
    buzzer.hello()
    exit

def follow_line():
    last_p = 0
    global p, ir, t1, t2, line
    while True:
        # do not proceed until it has been 1 ms from starting the run
        while(time.ticks_us() < t2 + 1000):
            pass
        ir_sensors.read_line_sensors()
        ir_sensors.run_line_sensors()
        t1 = t2
        t2 = time.ticks_us()
        line = ir_sensors.compute_line_calibrated()
        
        # postive p means robot is to right of line
        if line[1] > 300 and line[2] > 300 and line[3] > 300:
            if p < 0:
                l = 0
            else:
                l = 4000
        else:
            # estimate line position
            l = (1000*(1000-line[1]) + 2000*(1000-line[2]) + 3000*(1000-line[3]) + 4000*(1000-line[4])) // \
                (5000 - line[0] - line[1] - line[2] - line[3] - line[4])
        
        p = l - 2000        
        d = p - last_p
        last_p = p
        pid = p*90 + d*2000
        max_speed = 40000
        min_speed = 0
        left = max(min_speed, min(max_speed, max_speed - pid))
        right = max(min_speed, min(max_speed, max_speed + pid))
        motors.set_speeds(left, right)
    
display.fill(0)
display.text("Line Follower", 0, 0)
display.text("GET READY!!!", 0, 30)
display.show()

while buzzer.isPlaying():
    rgb_leds.show()
    time.sleep_ms(1)

#buzzer.playInBackground(song)
_thread.start_new_thread(follow_line, ())

def tri(x, min, max, t1, t2, period):
    x = x % period
    if x < t1:
        return min + x*(max-min)//t1;
    elif x < t2:
        return max - (x-t1)*(max-min)//(t2-t1);
    else:
        return 0

def siren1():
    global buzzer
    buzzer.pwm.duty_u16(32767)

    x = time.ticks_us()
    if x % 10000000 > 1000000:
        period = 2500000
        min = 727
        max = 1172
    else:
        period = 100000
        min = 900
        max = 1500
    buzzer.pwm.freq(tri(x, min, max, period//2,  period, period))
        
    T = 800000
    
    p1 = tri(x, 0, 255, T//6, T//3, T)
    p2 = tri(x+T//6, 0, 255, T//6, T//3, T)
    p3 = tri(x+T//3, 0, 255, T//6, T//3, T)
    p4 = tri(x+T//2, 0, 255, T//6, T//3, T)
    p5 = tri(x+T*2//3, 0, 255, T//6, T//3, T)
    p6 = tri(x+T*5//6, 0, 255, T//6, T//3, T)
    rgb_leds.set(0, [p4,0,p1])
    rgb_leds.set(1, [p2,0,p5])
    rgb_leds.set(2, [p1,0,p4])
    rgb_leds.set(3, [p4,0,p1])
    rgb_leds.set(4, [p5,0,p2])
    rgb_leds.set(5, [p1,0,p4])
    rgb_leds.show()

c = 0
while True:
    siren1()
    if c % 64 == 0:
        updateDisplay()
    time.sleep_ms(1)
    c += 1
