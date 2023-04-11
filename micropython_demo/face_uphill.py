# This demo uses the accelerometer on the 3pi+ to detect whether it is on a
# slanted surface.  If it is on a slanted surface, then it uses the motors to
# face uphill.
#
# It also uses the encoders to avoid rolling down the surface.

from pololu_3pi_2040_robot import robot
from pololu_3pi_2040_robot.extras import editions
import time

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
    encoders.flip(True)
    max_speed = 1500
    kp = 140
    kd = 4
ke = 15

drive_motors = False
last_time_gyro_reading = None
turn_rate = 0.0    # degrees per second
robot_angle = 0.0  # degrees
target_angle = 0.0
tilted = False

def constrain_speed(speed):
  if speed < -max_speed: return -max_speed
  if speed > max_speed: return max_speed
  return speed

def draw_text():
  display.fill(0)
  if drive_motors:
        display.text("A: Stop motors", 0, 0, 1)
  else:
        display.text("A: Start motors", 0, 0, 1)
  display.text(f"ay:", 0, 24, 1)
  display.text(f"Robot:", 0, 32, 1)
  display.text(f"Target:", 0, 40, 1)
  display.text(f"Enc:", 0, 48, 1)
  display.text(edition, 0, 56, 1)

draw_text()
display.show()
time.sleep_ms(500)

while True:
    encoder_counts = sum(encoders.get_counts())

    if imu.gyro.data_ready():
        # Read the gyroscope and accelerometer.
        imu.gyro.read()
        imu.acc.read()

        # Update the robot's angle.
        turn_rate = imu.gyro.last_reading_dps[2]
        now = time.ticks_us()
        if last_time_gyro_reading:
            dt = time.ticks_diff(now, last_time_gyro_reading)
            robot_angle += turn_rate * dt / 1000000
        last_time_gyro_reading = now

        # Detect if the robot is tilted more than 5 degrees.
        # If so, adjust the target angle slowly towards the uphill direction.
        ax = imu.acc.last_reading_g[0]
        ay = imu.acc.last_reading_g[1]
        tilted = ax * ax + ay * ay > 0.007596  # sin(5 deg)^2 = 0.007596
        if tilted:
            angle_increment = 0.8 if abs(ay > 0.1) or ax < 0 else 0.4
            if ay < 0:
                target_angle -= angle_increment
            else:
                target_angle += angle_increment

    # If the user presses button A, toggle whether the motors are on.
    if button_a.check() == True:
        while button_a.check() != False: pass  # wait for release
        drive_motors = not drive_motors
        if drive_motors:
            display.fill(1)
            display.text("Spinning", 30, 20, 0)
            display.text("WATCH OUT", 27, 30, 0)
            display.show()
            time.sleep_ms(500)
        draw_text()
        encoders.get_counts(reset=True)
        target_angle = robot_angle
        last_time_gyro_reading = time.ticks_us()

    # Show the current angle in degrees.
    display.fill_rect(48, 24, 72, 8 * 4, 0)
    display.text(f"{ay:>9.3f}",           48, 24, 1)
    display.text(f"{robot_angle:>9.3f}",  48, 32, 1)
    display.text(f"{target_angle:>9.3f}", 48, 40, 1)
    display.text(f"{encoder_counts:>5}",  48, 48, 1)
    display.show()

    if drive_motors:
        # Turn towards the target angle.
        turn_speed = (target_angle - robot_angle) * kp - turn_rate * kd

        # Avoid rolling downhill.
        forward_speed = constrain_speed(-encoder_counts * ke)

        left_speed = constrain_speed(forward_speed - turn_speed)
        right_speed = constrain_speed(forward_speed + turn_speed)
        motors.set_speeds(left_speed, right_speed)
    else:
        motors.off()

    yellow_led.value(drive_motors)

