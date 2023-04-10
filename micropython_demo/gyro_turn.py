# This example executes a 90-degree turn using the robot's gyroscope.
#
# In the "Choose edition" menu, use the A and C buttons to select what type of
# 3pi+ robot you have and then press B to confirm.
#
# Do not move the robot while it says "Calibrating..." on the screen.
#
# After the gyro calibration is done, press button A to turn one way or
# button C to turn the other way.

from pololu_3pi_2040_robot import robot
from pololu_3pi_2040_robot.extras import editions
import time

enable_data_logging = True
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
    kp = 160
    kd = 4
elif edition == "Turtle":   # TODO: tune
    max_speed = 6000
    kp = 200
    kd = 0
elif edition == "Hyper":    # TODO: tune
    motors.flip_left(True)
    motors.flip_right(True)
    max_speed = 1500
    kp = 200
    kd = 0

# Note: This calibration is not needed in many applications because the
# uncalibrated readings can only drift by about 1 degree per second.
display.fill(0)
display.text("Calibrating...", 0, 0, 1)
display.show()
time.sleep_ms(500)
calibration_start = time.ticks_ms()
stationary_gz = 0.0
reading_count = 0
while time.ticks_diff(time.ticks_ms(), calibration_start) < 1000:
    if imu.gyro.data_ready():
        imu.gyro.read()
        stationary_gz += imu.gyro.last_reading_dps[2]
        reading_count += 1
stationary_gz /= reading_count

drive_motors = False
last_time_gyro_reading = None
turn_rate = 0.0
robot_angle = 0.0
target_angle = 0.0
last_time_far_from_target = None
log = None
log_start_time = None

def log_time():
    return time.ticks_diff(time.ticks_us(), log_start_time)

def draw_text():
    display.fill(0)
    if drive_motors:
        display.text("A: Stop motors", 0, 0, 1)
        display.text("C: Stop motors", 0, 8, 1)
    else:
        display.text(f"A: Turn {angle_to_turn} deg", 0, 0, 1)
        display.text(f"C: Turn {-angle_to_turn} deg", 0, 8, 1)
    display.text(f"Angle:", 0, 32, 1)
    if log: display.text("Logging", 0, 48, 1)
    display.text(edition, 0, 56, 1)

def handle_turn_or_stop(button, angle):
    global target_angle, drive_motors
    global last_time_far_from_target, last_time_gyro_reading
    global log, log_start_time
    target_angle = robot_angle + angle
    drive_motors = not drive_motors
    if drive_motors:
        while button.check() != False: pass  # wait for release
        display.fill(1)
        display.text("Spinning", 30, 20, 0)
        display.text("WATCH OUT", 27, 30, 0)
        display.show()
        time.sleep_ms(500)
        if enable_data_logging:
            log = open("gyro_turn.log", "w")
            # Expand the file to 16 KB so future writes are fast.
            blank_kb = "\n" * 1024
            for i in range(16): log.write(blank_kb)
            log.seek(0, 0)
            print("hi", file=log)
            log_start_time = time.ticks_us()
        last_time_far_from_target = time.ticks_ms()
    draw_text()
    last_time_gyro_reading = time.ticks_us()

draw_text()

while True:
    if imu.acc.data_ready():
        imu.acc.read()

    # Update the angle and the turn rate.
    if imu.gyro.data_ready():
        imu.gyro.read()
        turn_rate = imu.gyro.last_reading_dps[2] - stationary_gz  # degrees per second
        now = time.ticks_us()
        if last_time_gyro_reading:
            dt = time.ticks_diff(now, last_time_gyro_reading)
            robot_angle += turn_rate * dt / 1000000
        last_time_gyro_reading = now
        if log:
            diff = robot_angle - target_angle
            a = imu.acc.last_reading_g
            print(f"{log_time()},{diff:.3f},{a[0]:.3f},{a[1]:.3f}", file=log)

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

    # Take care of closing the log file.
    if log and not drive_motors:
        log.close()
        log = None
        draw_text()

    # Update the display.
    display.fill_rect(48, 32, 72, 8, 0)
    display.text(f"{robot_angle - target_angle:>9.3f}", 48, 32, 1)
    display.show()

    # Drive motors.
    if drive_motors:
        speed = (robot_angle - target_angle) * kp + turn_rate * kd
        if speed > max_speed: speed = max_speed
        if speed < -max_speed: speed = -max_speed
        motors.set_speeds(speed, -speed)
        yellow_led.on()
    else:
        motors.off()
        yellow_led.off()
