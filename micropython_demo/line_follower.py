import time
import random
import rp2
from machine import Pin
from pololu_3pi_plus_2040_robot import robot
import _thread
from array import *

display = robot.Display()
motors = robot.Motors()
line_sensors = robot.LineSensors()

# Note: It's not safe to use Button B in a
# multi-core program.
button_a = robot.ButtonA()

display.fill(0)
display.text("Line Follower", 0, 0)
display.text("Place on line", 0, 20)
display.text("and press A to", 0, 30)
display.text("calibrate.", 0, 40)
display.show()

while not button_a.check():
    pass
    
display.fill(0)
display.show()
time.sleep_ms(500)

motors.set_speeds(2000, -2000)
for i in range(50):
    line_sensors.calibrate()
    time.sleep_ms(20)

motors.off()
time.sleep_ms(200)

motors.set_speeds(-2000, 2000)
for i in range(100):
    line_sensors.calibrate()
    time.sleep_ms(20)

motors.off()
time.sleep_ms(200)

motors.set_speeds(2000, -2000)
for i in range(50):
    line_sensors.calibrate()
    time.sleep_ms(20)

motors.off()

t1 = 0
t2 = time.ticks_us()
p = 0
max_speed = 0
line = []
starting = False
last_update_ms = 0

def updateDisplay():
    global display
    global line_sensors
    global t1, t2
    global c
    global p
    global line
    global starting
    
    display.fill(0)
    if starting:
        display.text("Line Follower", 0, 0)
    else:
        display.text("Press A", 0, 0)
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
    global p, ir, t1, t2, line, max_speed
    while True:
        line = line_sensors.read_calibrated()
        line_sensors.start_read()
        t1 = t2
        t2 = time.ticks_us()
        
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

        min_speed = 0
        left = max(min_speed, min(max_speed, max_speed - pid))
        right = max(min_speed, min(max_speed, max_speed + pid))
        motors.set_speeds(left, right)

_thread.start_new_thread(follow_line, ())

while True:
    t = time.ticks_ms()

    if time.ticks_diff(t, last_update_ms) > 200:
        last_update_ms = t
        updateDisplay()

    if button_a.check():
        starting = True
        start_ms = t

    if starting and time.ticks_diff(t, start_ms) > 1000:
        max_speed = 6000
