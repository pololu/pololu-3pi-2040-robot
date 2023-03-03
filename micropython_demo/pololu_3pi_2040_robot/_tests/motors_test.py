# Run this test with power off to verify that the Motor
# class does the right thing with the PWM registers.

from pololu_3pi_2040_robot import robot

motors = robot.Motors()
right = motors.right_motor_pwm
left = motors.left_motor_pwm
right_dir = motors.right_motor_dir
left_dir = motors.left_motor_dir

assert robot.motors.MAX_SPEED == robot.Motors.MAX_SPEED == motors.MAX_SPEED == 6000

assert left.freq() == 20833
assert right.freq() == 20833

motors.set_speeds(3000, 0)
assert left.duty_u16() == 32768, "left: 50% duty"
assert left_dir.value() == 0
assert right.duty_u16() == 0
assert right_dir.value() == 0

motors.set_speeds(6000, 3000)
assert left.duty_u16() == 65535, "left: 100% duty"
assert right.duty_u16() == 32768, "right: 50% duty"

motors.set_speeds(-6000, -3000)
assert left.duty_u16() == 65535, "left: -100% duty"
assert left_dir.value() == 1
assert right.duty_u16() == 32768, "right: -50% duty"
assert left_dir.value() == 1

motors.set_speeds(-2999.6, 2999.9)
assert left.duty_u16() == 32768, "left: rounding"
assert right.duty_u16() == 32768, "right: rounding"

motors.flip_left(True)
motors.set_speeds(-1, -1) # so it will really be 1, -1
assert left_dir.value() == 0
assert right_dir.value() == 1

motors.flip_left(False)
motors.flip_right(True)
motors.set_speeds(1, 1) # so it will really be 1, -1
assert left.duty_u16() == 11
assert left_dir.value() == 0
assert right.duty_u16() == 11
assert right_dir.value() == 1

motors.set_speeds(0, 0)
assert left_dir.value() == 0, "left: do not change dir on zero"
assert right_dir.value() == 1, "right: do not change dir on zero"

motors.set_left_speed(600)
assert left.duty_u16() == 6554
assert right.duty_u16() == 0

motors.set_right_speed(300)
assert left.duty_u16() == 6554, "left: still on"
assert right.duty_u16() == 3277

motors.set_right_speed(1)
assert left.duty_u16() == 6554
assert right.duty_u16() == 11

motors.off()
assert left.duty_u16() == 0
assert right.duty_u16() == 0

print("Motors test passed")
