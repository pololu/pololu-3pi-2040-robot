from pololu_3pi_plus_2040_robot import robot
import random

buzzer = robot.Buzzer()
display = robot.Display()
rgb_leds = robot.RGBLEDs()
button_b = robot.ButtonB()

intro = "t70 l16 ms v15 O4 rd+d+d+ O6 d+d+d+ O4 d+d+d+ t60 v13 O6 d+d+d+ O4 t50 v12 d+ O6 d+d+ t45 v10 O4 d+ O6 d+d+ rrr"
song = "t108 l16 ms v15 " + \
    "O5 ms l16 dO5d+d+>d+ d+>d+c+>d+ " + \
    "v15 mlO3g+32>d+32 v12 O5ms>d+b>d+a+>d+ v15 mlO3b32>g+32 v12 msO5>d+g>d+g+>d+" + \
    "v15 mlO4 d+32a+32 v12 mso5>d+d+>d+d+>d+ v15 mlO4g32a+32 v12 msO5>d+d+>d+c+>d+" + \
    "v14 mlO4g+32b32 v11 msO5>d+b>d+a+>d+ v15 mlO3b32>f32 v11 msO5>d+g>d+g+>d+" + \
    "v14 mlO4d+32g32 v11 msO5>d+<d+d+d+>d+ v13 d+>d+d+>d+c+>d+" + \
    "v13 mlO3g+32>d+32 v10 msO5>d+b>d+a+>d+ v13 mlO3b32>g+32 v10 msO5 >d+g>d+g+>d+" + \
    "v13 mlO4d+32a+32 v10 msO5>d+d+>d+d+>d+ v13 mlO4g32a+32 v10 msO5>d+d+>d+c+>d+" + \
    "v12 mlO4g+32b32 v9 msO5>d+g+b>d+>d+ v12 mlO4d+32g32 v9 msO5>d+ga+>d+>d+" + \
    "v15 t100 ml O4 <g+d+>b>g+ t95 d+32r32>d+32r32 d+4"

last_f = 0
up = False
def set_leds(v, f):
    global last_f, up

    v2 = v*v/16/16
    r = (500-f)*v2
    g = (1000-f)*v2
    b = (f-1000)*v2
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    print([r, g, b])

    if f > last_f and v != 0 and last_f != 0:
        up = True
    elif f < last_f and v != 0:
        up = False
    if v != 0:
      last_f = f

    x = random.randint(1,3)

    if not up:
        rgb_leds.set(0, [r,g,b] if x & 1 else [0,0,0])
        rgb_leds.set(1, [r,g,b] if x & 2 else [0,0,0])
        rgb_leds.set(2, [r,g,b] if x & 1 else [0,0,0])
        rgb_leds.set(3, [0,0,0])
        rgb_leds.set(4, [0,0,0])
        rgb_leds.set(5, [0,0,0])
    else:
        rgb_leds.set(0, [0,0,0])
        rgb_leds.set(1, [0,0,0])
        rgb_leds.set(2, [0,0,0])
        rgb_leds.set(3, [r,g,b] if x & 1 else [0,0,0])
        rgb_leds.set(4, [r,g,b] if x & 2 else [0,0,0])
        rgb_leds.set(5, [r,g,b] if x & 1 else [0,0,0])

    rgb_leds.show()

display.fill(0)
display.text("La campanella", 0, 0)
display.text("  by Franz Liszt", 0, 10)
display.text("Press B to stop.", 0, 50)
display.show()

buzzer.set_callback(set_leds)
buzzer.play_in_background(intro)

while not button_b.check():
    if not buzzer.is_playing():
        buzzer.play_in_background(song)

rgb_leds.off()
buzzer.off()
display.fill(0)
display.show()
