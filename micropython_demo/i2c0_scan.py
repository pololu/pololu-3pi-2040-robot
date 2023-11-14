from machine import I2C, Pin
from pololu_3pi_2040_robot import robot
from pololu_3pi_2040_robot.extras.menu import Menu

i2c = I2C(id=0, scl=Pin(5), sda=Pin(4), freq=400_000)
# Send low pulses on SCL to fix devices that are stuck
# driving SDA low.
for i in range(10):
    try: i2c.writeto(0, "")
    except OSError: pass

addrs = i2c.scan()

device_descriptions = {
    0x1E: ' (LIS3MDL)',
    0x6B: ' (LSM6DSO)',
}

print('I2C0 scan:')
options = []

for a in addrs:
    line = f"0x{a:02X}{device_descriptions.get(a, '')}"
    print(line)
    options += [line]

menu = Menu(options)
menu.top_message = 'I2C0: (^A Cv)'
menu.display = robot.Display()
menu.buzzer = robot.Buzzer()
menu.previous_button = robot.ButtonA()
menu.next_button = robot.ButtonC()

while True:
    menu.update()
