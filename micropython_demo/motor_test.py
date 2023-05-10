# This example provides an interface to test the motors and encoders.
#
# Holding button A or C causes the left or right motor to accelerate;
# releasing the button causes the motor to decelerate. Tapping the button
# while the motor is not running reverses the direction it runs.
#
# Encoder counts are displayed on the bottom two lines of the OLED.

from pololu_3pi_2040_robot import robot
import time

display = robot.Display()
button_a = robot.ButtonA()
button_b = robot.ButtonB()
button_c = robot.ButtonC()
motors = robot.Motors()
encoders = robot.Encoders()

display.text("Hold=run", 32, 0)
display.text("Tap=flip", 32, 8)
display.text("A", 8, 28)
display.text("C", 112, 28)
display.text("L: ", 24, 48)
display.text("R: ", 24, 56)

arrows = ["v", None, "^"]
left_dir = 1
right_dir = 1
left_speed = 0
right_speed = 0
last_update_time = 0
button_count_a = 0
button_count_c = 0

while True:
    # Update the LCD and motors every 50 ms.
    if time.ticks_diff(time.ticks_ms(), last_update_time) > 50:
        last_update_time = time.ticks_ms()

        if button_a.is_pressed():
            if button_count_a < 4:
                button_count_a += 1
            else:
                left_speed += 225
        else:
            if left_speed == 0 and 0 < button_count_a < 4:
                left_dir = -left_dir
            button_count_a = 0
            left_speed -= 450

        if button_c.is_pressed():
            if button_count_c < 4:
                button_count_c += 1
            else:
                right_speed += 225
        else:
            if right_speed == 0 and 0 < button_count_c < 4:
                right_dir = -right_dir
            button_count_c = 0
            right_speed -= 450

        if left_speed < 0: left_speed = 0
        if left_speed > motors.MAX_SPEED: left_speed = motors.MAX_SPEED
        if right_speed < 0: right_speed = 0
        if right_speed > motors.MAX_SPEED: right_speed = motors.MAX_SPEED

        motors.set_speeds(left_dir * left_speed, right_dir * right_speed)

        display.fill_rect(0, 0, 8, 64, 0)
        y = 28 + -left_dir * left_speed // 225
        display.text(arrows[left_dir + 1], 0, y)

        display.fill_rect(120, 0, 8, 64, 0)
        y = 28 + -right_dir * right_speed // 225
        display.text(arrows[right_dir + 1], 120, y)

        display.fill_rect(40, 48, 64, 16, 0)
        left_encoder, right_encoder = encoders.get_counts()
        display.text(f"{left_encoder:>8}", 40, 48)
        display.text(f"{right_encoder:>8}", 40, 56)

        display.show()
