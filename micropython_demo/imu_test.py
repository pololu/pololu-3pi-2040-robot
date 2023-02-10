import pololu_3pi_plus_2040_robot as robot
import time

imu = robot.IMU()
imu.reset()
imu.enable_default()

def format_reading(reading, format_spec):
    return ' '.join(f"{x:{format_spec}}" for x in reading)

while True:
    g = imu.gyro.read()
    a = imu.acc.read()
    m = imu.mag.read()
    print(f"G: {format_reading(g, '6.1f')}    A: {format_reading(a, '6.3f')}    M: {format_reading(m, '6.3f')}")
    time.sleep_ms(100)
