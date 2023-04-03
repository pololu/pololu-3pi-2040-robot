# Demo of music playing with callbacks for LED and display effects.

from pololu_3pi_2040_robot import robot

buzzer = robot.Buzzer()
display = robot.Display()
rgb_leds = robot.RGBLEDs()
button_b = robot.ButtonB()

rgb_leds.set_brightness(5)

intro = "t140 l8 ms v15 O4 rd+d+d+ O6 d+d+d+ " + \
        "O4 d+d+d+ t120 v13 O6 d+d+d+ " + \
        "O4 t100 v12 d+ O6 d+d+ t90 v10 O4 d+ O6 d+d+ rrr"
song = "t108 l16 ms v15 " + \
    "O5 ms l16 r4 dO5d+d+>d+ d+>d+c+>d+ " + \
    "v15 mlO3g+32>d+32 v12 O5ms>d+b>d+a+>d+ v15 mlO3b32>g+32 v12 msO5>d+g>d+g+>d+" + \
    "v15 mlO4 d+32a+32 v12 mso5>d+d+>d+d+>d+ v15 mlO4g32a+32 v12 msO5>d+d+>d+c+>d+" + \
    "v14 mlO4g+32b32 v11 msO5>d+b>d+a+>d+ v15 mlO3b32>f32 v11 msO5>d+g>d+g+>d+" + \
    "v14 mlO4d+32g32 v11 msO5>d+<d+d+d+>d+ v13 d+>d+d+>d+c+>d+" + \
    "v13 mlO3g+32>d+32 v10 msO5>d+b>d+a+>d+ v13 mlO3b32>g+32 v10 msO5 >d+g>d+g+>d+" + \
    "v13 mlO4d+32a+32 v10 msO5>d+d+>d+d+>d+ v13 mlO4g32a+32 v10 msO5>d+d+>d+c+>d+" + \
    "v12 mlO4g+32b32 v9 msO5>d+g+b>d+>d+ v12 mlO4d+32g32 v9 msO5>d+ga+>d+>d+" + \
    "v15 t100 ml O4 <g+d+>b>g+ t95 d+32r32>d+32r32 d+4"

def music_callback(i):
    update_display(buzzer.beats[i])

    # Set the LED brightness (0-255) according to the
    # note volume (0-128).
    value = min(255, buzzer.volumes[i]*2)

    # Start the hue at red (0) for a middle C (48) and
    # wrap around every 3 octaves (36 notes).
    hue = (buzzer.notes[i] - 48) * 360 // 36

    # Use lower saturation for longer note durations
    # (given in milliseconds).
    saturation = max(0, 255 - buzzer.durations[i] / 4)

    for led in range(6):
        rgb_leds.set_hsv(led, [hue, saturation, value])

    rgb_leds.show()

def update_display(elapsed_beats):
    display.fill(0)
    display.text("La campanella", 0, 0)
    display.text("  by Franz Liszt", 0, 10)

    # quarter = 20160, 6/8 time
    eigths = elapsed_beats//10080
    measure = measure_offset + 1 + eigths // 6
    beat = 1 + eigths % 6
    display.text(f"measure {measure} b {beat}", 0, 30)

    display.text("Press B to stop.", 0, 50)
    display.show()

buzzer.set_callback(music_callback)

measure_offset = 0
buzzer.play_in_background(intro)

try:
    while not button_b.check():
        if not buzzer.is_playing():
            measure_offset = 4
            buzzer.play_in_background(song)
finally:
    rgb_leds.off()
    buzzer.off()
    display.fill(0)
    display.show()
