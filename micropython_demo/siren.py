# A siren sound effect.

from pololu_3pi_2040_robot import robot
import time

rgb_leds = robot.RGBLEDs()
buzzer = robot.Buzzer()

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

while True:
    siren1()
