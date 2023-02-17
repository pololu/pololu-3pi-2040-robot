# Run this test with the 3pi on a white surface
# such as a piece of paper to verify that the
# library works.

import pololu_3pi_plus_2040_robot as robot
import time

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