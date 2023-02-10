import time
import random
import rp2
from machine import Pin
import pololu_3pi_plus_2040_robot as robot
import _thread
from array import *

display = robot.Display()
motors = robot.Motors()
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
    
    display.fill_rect(36, 64-int(line[4]*scale), 8, int(line[4]*scale), 1)
    display.fill_rect(48, 64-int(line[3]*scale), 8, int(line[3]*scale), 1)
    display.fill_rect(60, 64-int(line[2]*scale), 8, int(line[2]*scale), 1)
    display.fill_rect(72, 64-int(line[1]*scale), 8, int(line[1]*scale), 1)
    display.fill_rect(84, 64-int(line[0]*scale), 8, int(line[0]*scale), 1)

    display.show()

def follow_line():
    last_p = 0
    global p, ir, t1, t2, line
    ir_sensors.run_line_sensors()
    while True:
        ir_sensors.read_line_sensors()
        ir_sensors.run_line_sensors()
        t1 = t2
        t2 = time.ticks_us()
        line = ir_sensors.compute_line_calibrated()
        
        # postive p means robot is to right of line
        if line[1] < 700 and line[2] < 700 and line[3] < 700:
            if p < 0:
                l = 0
            else:
                l = 4000
        else:
            # estimate line position
            l = (1000*line[1] + 2000*line[2] + 3000*line[3] + 4000*line[4]) // \
                (line[0] + line[1] + line[2] + line[3] + line[4])
        
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

_thread.start_new_thread(follow_line, ())

while True:
    updateDisplay()
    time.sleep_ms(200)
