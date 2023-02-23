import machine
from pololu_3pi_plus_2040_robot import robot
import sys
import time

battery = robot.Battery()
bump_sensors = robot.BumpSensors()
button_b = robot.ButtonB()
button_c = robot.ButtonC()
buzzer = robot.Buzzer()
display = robot.Display()
encoders = robot.Encoders()
imu = robot.IMU()
motors = robot.Motors()
rgb_leds = robot.RGBLEDs()

BEEP_BROWNOUT = '<c8'
BEEP_WELCOME = '>g32>>c32'
BEEP_FAIL = '<g-8r8<g-8r8<g-8'
BEEP_PASS = '>l32c>e>g>>c8'

YELLOW = [255, 64, 0]
GREEN = [0, 255, 0]

def display_line_break(lines=1, show=True):
    display.scroll(0, -8 * lines)
    display.fill_rect(0, 64 - 8 * lines, 128, 8 * lines, 0)
    if show: display.show()

def display_centered_text(text, show=True):
    display.text(text, (128 - len(text) * 8) // 2, 56)
    if show: display.show()

# Custom exception for test errors
class TestError(Exception):
    pass

def show_test_error(test_error):
    sys.print_exception(test_error)

    display_line_break()
    display_centered_text('FAIL')
    display.show()

    for i in range(6):
        rgb_leds.set(i, [255, 0, 0])
    rgb_leds.show()

    buzzer.play_in_background(BEEP_FAIL)

def run_test():
    rgb_leds.set_brightness(2)

    display.fill(0)
    display_centered_text('3pi+ 2040')
    display_line_break()
    display_centered_text('Self Test')
    time.sleep_ms(500)

    #bump_sensors.calibrate() FIXME when this is made to work like 32U4 version
    import array
    bump_sensors.cal_min = array.array('H', [500,500])
    bump_sensors.cal_max = array.array('H', [0,0])

    display_line_break(2)
    display_centered_text('Press bumpers')
    while True:
        bump = bump_sensors.read_calibrated()
        if all(bump): break
        time.sleep_ms(10) # FIXME remove if issue with repeated reads is fixed
    display.fill_rect(0, 56, 128, 8, 0)
    display_centered_text('Bumpers OK')
    rgb_leds.set(5, YELLOW) # F
    rgb_leds.show()
    buzzer.play_in_background('!c32')
    time.sleep_ms(500)

    # test some voltages and IMU presence
    display_line_break(2)
    v = battery.get_level_millivolts()
    display_centered_text(f"VBAT {v:4} mV")
    if v < 4000 or v > 7000:
        raise TestError(f"VBAT out of range: {v} mV")
    rgb_leds.set(4, YELLOW) # E
    rgb_leds.show()
    time.sleep_ms(500)

    display_line_break(2)
    display_centered_text('IMU   ')
    imu.reset()
    if not imu.detect():
        raise TestError('IMU not detected')
    display_centered_text('    OK')
    rgb_leds.set(3, YELLOW) # D
    rgb_leds.show()
    time.sleep_ms(500)

    display_line_break(2)
    display_centered_text('Motors')
    rgb_leds.set(0, YELLOW) # A
    rgb_leds.show()
    imu.enable_default()
    imu.gyro.set_output_data_rate(833)
    imu.gyro.set_full_scale(2000)

    encoders.get_counts(reset=True)
    motors.set_speeds(1350, -1350)
    time.sleep_ms(250)

    imu.gyro.read()
    gyro_z = imu.gyro.last_reading_dps[2]

    motors.set_speeds(0, 0)
    time.sleep_ms(100)
    left, right = encoders.get_counts()
    display_line_break()
    display_centered_text(f"L={left} R={right}")
    display_line_break()
    display_centered_text(f"Gyro Z={gyro_z:.1f}")
    display_line_break()
    if gyro_z > -490 and gyro_z < -350 and \
            left > 212 and left < 288 and right > -288 and right < -212:
        edition = 'Standard'
    elif gyro_z > -126 and gyro_z < -84 and \
            left > 140 and left < 200 and right > -200 and right < -140:
        edition = 'Turtle'
    elif gyro_z > 665 and gyro_z < 1190 and \
            left > 130 and left < 370 and right > -370 and right < -130:
        edition = 'Hyper'
    else:
        raise TestError("Couldn't detect edition: L={left} R={right} Gyro Z={gyro_z:.1f}")
    display_line_break()
    display_centered_text(f"{edition}?")
    display_line_break()
    display_centered_text('B=Yes C=No')
    rgb_leds.set(1, YELLOW) # B
    rgb_leds.show()

    while True:
        if button_b.is_pressed():
            buzzer.play_in_background('!e32')
            break
        if button_c.is_pressed():
            buzzer.play_in_background('!g32')
            raise TestError('Edition mismatch')

    display_line_break(2)
    display_centered_text('PASS')
    for i in range(6):
        rgb_leds.set(i, GREEN)
    rgb_leds.show()
    buzzer.play_in_background(BEEP_PASS)

try:
    run_test()
except TestError as te:
    show_test_error(te)
finally:
    while True:
        machine.idle()
