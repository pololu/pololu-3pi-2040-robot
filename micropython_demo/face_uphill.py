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
#imu.acc.set_output_data_rate(12.5)  # TODO: needed?

edition = editions.select()

# 12.5 Hz ODR: oscillation happened around 16000, with period of 0.25 s.
# Regular ODS: oscillation happened at 25000, with period of ~0.125 s
if edition == "Standard":   # TODO: tune
    max_speed = 3000
    ke = 15
    kp = 20000
    # TODO: kp = 12800, kd = 500
elif edition == "Turtle":   # TODO: tune
    max_speed = 6000
    ke = 15
    kp = 8000
elif edition == "Hyper":    # TODO: tune
    motors.flip_left(True)
    motors.flip_right(True)
    max_speed = 1500
    ke = 15
    kp = 8000

last_display_time = 0
log = None
log_start_time = None
x = 0
y = 0
gz = 0
last_acc_read_time = 0
sy = 0

def constrain_speed(speed):
  if speed < -max_speed: return -max_speed
  if speed > max_speed: return max_speed
  return speed

def draw_text():
  display.fill(0)
  display.text(f"x:", 0, 24, 1)
  display.text(f"y:", 0, 32, 1)
  display.text(f"e:", 0, 40, 1)
  if log: display.text("Logging", 0, 48, 1)
  display.text(edition, 0, 56, 1)

def log_time():
    return time.ticks_diff(time.ticks_us(), log_start_time)

draw_text()
display.show()

time.sleep_ms(500)  # Delay before running motors.

while True:
    # Read the accelerometer and encoders.
    if imu.acc.data_ready():
        imu.acc.read()
        dt = time.ticks_diff(time.ticks_us(), last_acc_read_time)
        sy = (imu.acc.last_reading_g[1] - y) * 1000000 / dt
        x = imu.acc.last_reading_g[0]
        y = imu.acc.last_reading_g[1]
        encoder_counts = sum(encoders.get_counts())
        if log: print(f"{log_time()},{x:.3f},{y:.3f},{sy:.4f},{gz:.3f}", file=log)
        last_acc_read_time = time.ticks_us()

    if imu.gyro.data_ready():
        imu.gyro.read()
        gz = imu.gyro.last_reading_dps[2]

    # If the user pressed button C, toggle data logging.
    if button_c.check() == True:
        if log:
            log.close()
            log = None
        else:
            log = open("face_uphill.log", "w")
            log_start_time = time.ticks_us()
        draw_text()

    # Display sensor readings on the OLED every 150 ms.
    if time.ticks_diff(time.ticks_ms(), last_display_time) > 150:
        last_display_time = time.ticks_ms()
        display.fill_rect(32, 24, 48, 24, 0)
        display.text(f"{x:>6.3f}", 32, 24, 1)
        display.text(f"{y:>6.3f}", 32, 32, 1)
        display.text(f"{encoder_counts:>5}", 32, 40, 1)
        display.show()

    # sin(5 deg)^2 = 0.007596
    if x * x + y * y > 0.007596:
        # We are on an incline of more than 5 degrees.
        if x < 0:
          # We are more than 90 degrees away from uphill, so just turn at
          # the maximum speed.
          if y < 0:
            turn_speed = -max_speed
          else:
            turn_speed = max_speed
        else:
          # We are within 90 degrees of facing uphill, so use a feedback
          # algorithm to face uphill.
          turn_speed = y * kp

        yellow_led.on()
    else:
        # We are not on a noticeable incline, so don't turn.
        turn_speed = 0
        yellow_led.off()

    # If the robot rolls downhill, the encoder counts will become negative,
    # resulting in a positive forward_speed to counteract the rolling.
    forward_speed = constrain_speed(-encoder_counts * ke)

    left_speed = constrain_speed(forward_speed - turn_speed)
    right_speed = constrain_speed(forward_speed + turn_speed)
    motors.set_speeds(left_speed, right_speed)
