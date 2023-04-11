# This example make the robot turn 90 degrees using the gyroscope.
#
# In the "Choose edition" menu, use the A and C buttons to select what type of
# 3pi+ robot you have and then press B to confirm.  Then press button A or C
# to make the robot turn.
#
# If you need the turn to be more accurate, you might consider calibrating the
# gyro (see rotation_resist.py), but that doesn't make much difference for
# short turns.

from pololu_3pi_2040_robot import robot
from pololu_3pi_2040_robot.extras import editions
import time

angle_to_turn = 90

motors = robot.Motors()
encoders = robot.Encoders()
button_a = robot.ButtonA()
button_c = robot.ButtonC()
display = robot.Display()
yellow_led = robot.YellowLED()

display.fill(0)
display.text("Starting IMU...", 0, 0, 1)
display.show()
imu = robot.IMU()
imu.reset()
imu.enable_default()

edition = editions.select()
if edition == "Standard":
    max_speed = 3000
    kp = 140
    kd = 4
elif edition == "Turtle":
    max_speed = 6000
    kp = 350
    kd = 7
elif edition == "Hyper":
    motors.flip_left(True)
    motors.flip_right(True)
    max_speed = 1500
    kp = 140
    kd = 4

drive_motors = False
last_time_gyro_reading = None
turn_rate = 0.0     # degrees per second
robot_angle = 0.0   # degrees
target_angle = 0.0
last_time_far_from_target = None

def draw_text():
    display.fill(0)
    if drive_motors:
        display.text("A: Stop motors", 0, 0, 1)
        display.text("C: Stop motors", 0, 8, 1)
    else:
        display.text(f"A: Turn {angle_to_turn} deg", 0, 0, 1)
        display.text(f"C: Turn {-angle_to_turn} deg", 0, 8, 1)
    display.text(f"Angle:", 0, 32, 1)
    display.text(edition, 0, 56, 1)

def handle_turn_or_stop(button, angle):
    global target_angle, drive_motors
    global last_time_far_from_target, last_time_gyro_reading
    target_angle = robot_angle + angle
    drive_motors = not drive_motors
    if drive_motors:
        while button.check() != False: pass  # wait for release
        display.fill(1)
        display.text("Spinning", 30, 20, 0)
        display.text("WATCH OUT", 27, 30, 0)
        display.show()
        time.sleep_ms(500)
        last_time_far_from_target = time.ticks_ms()
    draw_text()
    last_time_gyro_reading = time.ticks_us()

draw_text()

while True:
    # Update the angle and the turn rate.
    if imu.gyro.data_ready():
        imu.gyro.read()
        turn_rate = imu.gyro.last_reading_dps[2]  # degrees per second
        now = time.ticks_us()
        if last_time_gyro_reading:
            dt = time.ticks_diff(now, last_time_gyro_reading)
            robot_angle += turn_rate * dt / 1000000
        last_time_gyro_reading = now

    # Respond to button presses.
    if button_a.check() == True:
        handle_turn_or_stop(button_a, angle_to_turn)
    if button_c.check() == True:
        handle_turn_or_stop(button_c, -angle_to_turn)

    # Decide whether to stop the motors.
    if drive_motors:
        far_from_target = abs(robot_angle - target_angle) > 3
        if far_from_target:
            last_time_far_from_target = time.ticks_ms()
        elif time.ticks_diff(time.ticks_ms(), last_time_far_from_target) > 250:
            drive_motors = False
            draw_text()

    # Show the current angle in degrees.
    display.fill_rect(48, 32, 72, 8, 0)
    display.text(f"{robot_angle - target_angle:>9.3f}", 48, 32, 1)
    display.show()

    # Drive motors.
    if drive_motors:
        turn_speed = (target_angle - robot_angle) * kp - turn_rate * kd
        if turn_speed > max_speed: turn_speed = max_speed
        if turn_speed < -max_speed: turn_speed = -max_speed
        motors.set_speeds(-turn_speed, turn_speed)
    else:
        motors.off()

    yellow_led.value(drive_motors)
