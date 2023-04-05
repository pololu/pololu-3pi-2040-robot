# TODO: tune the PID parameters for standard edition
# TODO: make it work well on the other editions too (with a menu to select them?)

from pololu_3pi_2040_robot import robot
import time

motors = robot.Motors()
button_a = robot.ButtonA()
display = robot.Display()
yellow_led = robot.YellowLED()

imu = robot.IMU()
imu.reset()
imu.enable_default()

display.fill(0)
display.text("Calibrating...", 0, 0, 1)
display.show()
time.sleep_ms(500)   # skip spurious readings at startup
start = time.ticks_ms()
stationary_gz = 0.0
reading_count = 0
while time.ticks_diff(time.ticks_ms(), start) < 3000:
    if imu.gyro.data_ready():
        imu.gyro.read()
        stationary_gz += imu.gyro.last_reading_dps[2]
        reading_count += 1
stationary_gz /= reading_count

drive_motors = False
last_time = None
angle = 0.0

def draw_options():
  display.fill(0)
  a = "A: Stop motors" if drive_motors else "A: Start motors"
  display.text(a, 0, 0, 1)

draw_options()

while True:
    # Update the angle and the turn rate.
    if imu.gyro.data_ready():
        imu.gyro.read()
        turn_rate = imu.gyro.last_reading_dps[2] - stationary_gz  # degrees per second
        now = time.ticks_us()
        if last_time:
            dt = time.ticks_diff(now, last_time)
            angle += turn_rate * dt / 1000000
        last_time = now

    # If the user presses button A, toggle whether the motors are on.
    if button_a.check() == True:
        drive_motors = not drive_motors
        if drive_motors:
            display.fill(1)
            display.text("Spinning", 30, 20, 0)
            display.text("WATCH OUT", 27, 30, 0)
            display.show()
            time.sleep_ms(500)
        draw_options()
        last_time = time.ticks_us()

    # Show the current angle in degrees.
    display.fill_rect(0, 32, 72, 8, 0)
    display.text("{:>9.3f}".format(angle), 0, 32, 1)
    display.show()

    # Drive motors
    if drive_motors:
        speed = angle / 30 * motors.MAX_SPEED + turn_rate / 50
        if speed > 3000: speed = 3000
        if speed < -3000: speed = -3000
        motors.set_speeds(speed, -speed)
        yellow_led.on()
    else:
        motors.off()
        yellow_led.off()
