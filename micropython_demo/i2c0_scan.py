from machine import I2C, Pin
from zumo_2040_robot import robot

display = robot.Display()

i2c = I2C(id=0, scl=Pin(5), sda=Pin(4))
addrs = i2c.scan()

device_descriptions = {
    0x1E: ' (LIS3MDL)',
    0x6B: ' (LSM6DSO)',
}

print('I2C0 scan:')
display.fill(0)
display.text('I2C0 scan:', 0, 0)

y = 0
for a in addrs:
    line = f"0x{a:02X}{device_descriptions.get(a, '')}"
    print(line)
    if y < 56:
        y += 8
        display.text(line, 0, y)

if len(addrs) > 7:
    display.fill_rect(0, 56, 128, 8, 0)
    display.text(f"+{len(addrs) - 6} more...", 0, 56)

display.show()