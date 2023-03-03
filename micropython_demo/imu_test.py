# Runs all the IMU sensors, displaying values on the screen and
# printing them to the USB serial port.

from pololu_3pi_2040_robot import robot
import time

display = robot.Display()
imu = robot.IMU()
imu.reset()
imu.enable_default()

def format_reading(reading, format_spec):
    return ' '.join(f"{x:{format_spec}}" for x in reading)

while True:
    imu.read()
    g = imu.gyro.last_reading_dps
    a = imu.acc.last_reading_g
    m = imu.mag.last_reading_gauss
    print(f"G: {format_reading(g, '6.1f')}    A: {format_reading(a, '6.3f')}    M: {format_reading(m, '6.3f')}")

    display.fill(0)
    display.text("gyro (dps):", 0, 0)
    display.text("{:>5.1f} {:>5.1f}{:>5.1f}".format(*g), 0, 10)
    display.text("acc (g):", 0, 23)
    display.text("{:>5.2f} {:>5.2f}{:>5.2f}".format(*a), 0, 33)
    display.text("mag (gauss):", 0, 47)
    display.text("{:>5.2f} {:>5.2f}{:>5.2f}".format(*m), 0, 57)
    display.show()

    time.sleep_ms(100)
