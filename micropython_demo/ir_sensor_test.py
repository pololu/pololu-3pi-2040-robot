import time
import pololu_3pi_plus_2040_robot as robot

ir_sensors = robot.IRSensors()
display = robot.Display()
last_update = 0

while True:
    display.text('IR Sensor Test', 0, 0)
    
    bump = ir_sensors.read_bump_sensors()
    ir_sensors.run_line_sensors()
    time.sleep_ms(1)
    
    start = time.ticks_us()
    line = ir_sensors.read_line_sensors()
    stop = time.ticks_us()
    
    if stop - last_update > 200000:
        display.fill_rect(0, 10, 128, 10, 0)
        display.text("read time: {}us".format(stop-start), 0, 10)
        last_update = stop
    
    # 64-40 = 24
    scale = 24/1023
    
    display.fill_rect(0, 32, 128, 32, 0)
    display.fill_rect(0, 64-int(bump[1]*scale), 8, int(bump[1]*scale), 1)
    
    display.fill_rect(36, 64-int(line[4]*scale), 8, int(line[4]*scale), 1)
    display.fill_rect(48, 64-int(line[3]*scale), 8, int(line[3]*scale), 1)
    display.fill_rect(60, 64-int(line[2]*scale), 8, int(line[2]*scale), 1)
    display.fill_rect(72, 64-int(line[1]*scale), 8, int(line[1]*scale), 1)
    display.fill_rect(84, 64-int(line[0]*scale), 8, int(line[0]*scale), 1)
    
    display.fill_rect(120, 64-int(bump[0]*scale), 8, int(bump[0]*scale), 1)
    display.show()