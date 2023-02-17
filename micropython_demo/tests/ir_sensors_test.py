# Run this test with the 3pi on a white surface
# such as a piece of paper to verify that the
# library works.

import pololu_3pi_plus_2040_robot as robot
import time
import array

sensors = robot.IRSensors()

#### LINE SENSORS
# test without starting the read ahead of time
start = time.ticks_us()
data = sensors.read_line_sensors()
stop = time.ticks_us()

print("Blocking read: {}us {}".format(stop - start, data))
assert stop - start > 1000, "should take time to measure"
assert min(data) > 100
assert max(data) < 900
assert sensors._state == 0

# test starting the read ahead of time
sensors.read_line_sensors() # this line seems to help warm it up and speed up the timing
sensors.start_read_line_sensors()
time.sleep_ms(2)
start = time.ticks_us()
data2 = sensors.read_line_sensors()
stop = time.ticks_us()

print("Non-blocking read: {}us {}".format(stop - start, data2))
assert stop - start < 500, "fast non-blocking read"
assert min(data2) > 100
assert max(data2) < 900
assert sensors._state == 0

# check that the values are close
for i in range(5):
    assert abs(data[i] - data2[i]) < 20
    
# fake calibration
sensors.line_cal_min = array.array('H', [data[0]-100, data[1]+100, data[2]-100, 0, 0])
sensors.line_cal_max = array.array('H', [data[0]+100, data[1]+200, data[2]-90, 0, 1023])
sensors.read_line_sensors_calibrated() # this line seems to help warm it up and speed up the timing
sensors.start_read_line_sensors()
time.sleep_ms(2)
start = time.ticks_us()
data = sensors.read_line_sensors_calibrated()
stop = time.ticks_us()

print("Calibratred read: {}us {}".format(stop - start, data))
#assert stop - start < 500, "fast non-blocking read"
assert data[0] > 400 and data[0] < 600, "calibrated"
assert data[1] == 0, "out of range low"
assert data[2] == 1000, "out of range high"
assert data[3] == 0, "division by zero"
assert abs(data[4] - data2[4]) < 20, "uncalibrated" 

#### BUMP SENSORS
# test without starting the read ahead of time
start = time.ticks_us()
data = sensors.read_bump_sensors()
stop = time.ticks_us()

print("Blocking read: {}us {}".format(stop - start, data))
assert stop - start > 1000, "should take time to measure"
assert min(data) > 100
assert max(data) < 900
assert sensors._state == 0

# test starting the read ahead of time
sensors.start_read_bump_sensors()
time.sleep_ms(2)
start = time.ticks_us()
data2 = sensors.read_bump_sensors()
stop = time.ticks_us()

print("Non-blocking read: {}us {}".format(stop - start, data2))
assert stop - start < 500, "fast non-blocking read"
assert min(data2) > 100
assert max(data2) < 900
assert sensors._state == 0

# check that the values are close
for i in range(2):
    assert abs(data[i] - data2[i]) < 20
    
# fake calibration
sensors.bump_cal_min = array.array('H', [data[0]-100, data[1]-10])
sensors.bump_cal_max = array.array('H', [data[0]+10, data[1]+100])
sensors.read_bump_sensors_calibrated() # this line seems to help warm it up and speed up the timing
sensors.start_read_bump_sensors()
time.sleep_ms(2)
start = time.ticks_us()
data = sensors.read_bump_sensors_calibrated()
stop = time.ticks_us()

print("Calibratred read: {}us {}".format(stop - start, data))
#assert stop - start < 500, "fast non-blocking read"
assert data[0] == 1000, "calibrated high"
assert data[1] == 0, "calibrated low"