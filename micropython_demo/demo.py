import time
import random
import rp2
from machine import Pin
import pololu_3pi_plus_2040_robot as robot
import _thread

button_a = robot.ButtonA()
button_b = robot.ButtonB()
button_c = robot.ButtonC()

rgb_leds = robot.RGBLEDs()
led = robot.YellowLED()
motors = robot.Motors()
motors.set_speeds(0, 0)
encoders = robot.Encoders()
buzzer = robot.Buzzer()
battery = robot.Battery()
ir_sensors = robot.IRSensors()
display = robot.Display()

def dim():
    rgb_leds.set_brightness(3, 1)
    rgb_leds.set_brightness(4, 1)
    rgb_leds.set_brightness(5, 1)
    
def bright():
    rgb_leds.set_brightness(3, 31)
    rgb_leds.set_brightness(4, 31)
    rgb_leds.set_brightness(5, 31)

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

last_f = 0
up = False
def set_leds(v, f):
    global rgb_leds, last_f, up
    
    v2 = v*v/128/128
    
    c = random.randint(0, 3)
    if c == 0:
        r,g,b = 255,0,0
    elif c == 1:
        r,g,b = 0,255,0
    elif c == 2:
        r,g,b = 0,0,255
    elif c == 3:
        r,g,b = 128,0,255
    
    if f > last_f and v != 0 and last_f != 0:
        up = True
    elif f < last_f and v != 0:
        up = False
    
    x = random.randint(1,3)
    
    if not up:
        rgb_leds.set(0, [r,g,b] if x & 1 != 0 else [0,0,0])
        rgb_leds.set(1, [r,g,b] if x & 2 != 0 else [0,0,0])
        rgb_leds.set(2, [r,g,b] if x & 1 != 0 else [0,0,0])
        rgb_leds.set(3, [0,0,0])
        rgb_leds.set(4, [0,0,0])
        rgb_leds.set(5, [0,0,0])
    else:
        rgb_leds.set(0, [0,0,0])
        rgb_leds.set(1, [0,0,0])
        rgb_leds.set(2, [0,0,0])
        rgb_leds.set(3, [r,g,b] if x & 1 != 0 else [0,0,0])
        rgb_leds.set(4, [r,g,b] if x & 2 != 0 else [0,0,0])
        rgb_leds.set(5, [r,g,b] if x & 1 != 0 else [0,0,0])
    if v != 0:
        last_f = f
    rgb_leds.show()

def song():
    snow = "t220 msc6mlc12 o5 msc6mlc12 o4 b-ag fc.r msc6mlc12 g.f8g.f8 ec.r8" +\
           "t220 d o5 msd6mld12 c o4 b-a g2r o5 e6d12 mscml c6 o4 b-12 msaml a6g12f2r" +\
           "t220 c g6a12ge>c g2r e6g12 msfml f6e12dc6d12 e2r" +\
           "t220 e6f12 ga6g12e>c g2.r > c6b12aba6b12>c2r"
    buzzer.setCallback(set_leds)
    bright()
    buzzer.play_in_background(snow)

dim()

pulse = [0,1,1,1,2,2,4,6,9,12,16,20,25,30,36,49,56,64,72,81,90,100,110,121,131,144,169,180,196,210,225,240,255]
pulse = pulse + pulse[::-1]

def update():
    global display
    global encoders
    global pulse
    global ir_sensors
    global run_motors

    display.fill(0)
    display.text('3pi+ 2040 OLED!', 0, 0)
    display.text('Buttons: ' + ('A' if button_a.is_pressed() else '_') + ' ' + ('B' if button_b.is_pressed() else '_') + ' ' + ('C' if button_c.is_pressed() else '_'), 0, 10)
    display.text('VBAT: '+str(battery.get_level_millivolts())+'    ', 0, 20)
    c = encoders.get_counts()
    display.text('Enc: '+str(c[0])+' '+str(c[1]), 0, 30)
    
    bump = ir_sensors.read_bump_sensors()
    ir_sensors.run_line_sensors()
    time.sleep_ms(1)
    line = ir_sensors.read_line_sensors()
    
    # 64-40 = 24
    scale = 24/1023
    display.fill_rect(0, 64-int(bump[1]*scale), 8, int(bump[1]*scale), 1)
    
    display.fill_rect(36, 64-int(line[4]*scale), 8, int(line[4]*scale), 1)
    display.fill_rect(48, 64-int(line[3]*scale), 8, int(line[3]*scale), 1)
    display.fill_rect(60, 64-int(line[2]*scale), 8, int(line[2]*scale), 1)
    display.fill_rect(72, 64-int(line[1]*scale), 8, int(line[1]*scale), 1)
    display.fill_rect(84, 64-int(line[0]*scale), 8, int(line[0]*scale), 1)
    
    display.fill_rect(120, 64-int(bump[0]*scale), 8, int(bump[0]*scale), 1)
    display.show()
    
    if not buzzer.is_playing():
        dim()
        rgb_leds.set(0, [255, 255, 0] if button_a.is_pressed() else [0, 0, 0])
        rgb_leds.set(1, [0, 255, 255] if button_b.is_pressed() else [0, 0, 0])
        rgb_leds.set(2, [255, 0, 255] if button_c.is_pressed() else [0, 0, 0])

        b = pulse[int(time.ticks_ms()/50)%len(pulse)]
        rgb_leds.set(3, [b,b,b])
        rgb_leds.set(4, [b,b,b])
        rgb_leds.set(5, [b,b,b])
        rgb_leds.show()
    
    if button_a.is_pressed():
        spin()
        
    if button_b.is_pressed():
        bright()
        display.text('_', 88, 10, 0) # erase the _
        display.text('B', 88, 10)
        display.show()
        
        buzzer.off()
        while(button_b.is_pressed()):
            siren1()
        dim()
        buzzer.off()
        
    if button_c.is_pressed() and not buzzer.is_playing():
        song()

def nullCallback(v, f):
    pass

run_motors = False
def spin():
    display.fill(1)
    display.text("Spinning", 30, 20, 0)
    display.text("WATCH OUT", 27, 30, 0)
    display.show()
    
    rgb_leds.off()
    
    buzzer.setCallback(nullCallback)
    buzzer.play("L16 o4 cfa>cra>c4r4")
    bright()
    
    circus =\
        "! O6 L8 T180" +\
        "MS aa- L16 ML ga-gg- L8 MS fe ML e- MS e fe L16 ML e-ee-d L8 MS d-c ML <b MS c" +\
        "MS e L16 <b<b L8 ML <b-<b" +\
        "MS e L16 <b<b L8 ML <b-<b" +\
        "L16 <a-<a<b-<bcd-de- L8 MS fe ML e- MS e"
    
    rgb_leds.set(0, [255, 0, 0])
    rgb_leds.set(1, [192, 64, 0])
    rgb_leds.set(2, [128, 128, 0])
    rgb_leds.set(3, [0, 255, 0])
    rgb_leds.set(4, [0, 0, 255])
    rgb_leds.set(5, [128, 0, 128])
    rgb_leds.show()
    
    buzzer.play_in_background(circus)
    
    global motors, led
    led.on()
    for i in range(0, 65535, 2500):
        motors.set_speeds(i, -i)
        time.sleep_ms(50)
    led.off()
    for i in range(65535, 0, -2500):
        motors.set_speeds(i, -i)
        time.sleep_ms(50)

    led.on()
    for i in range(0, -65535, -2500):
        motors.set_speeds(i, -i)
        time.sleep_ms(50)
    led.off()
    for i in range(-65535, 0, 2500):
        motors.set_speeds(i, -i)
        time.sleep_ms(50)
    motors.set_speeds(0,0)
    dim()
    buzzer.off()

while True:
    update()

