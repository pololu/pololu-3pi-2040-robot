import pololu_3pi_plus_2040_robot as robot

motors = robot.Motors()
right = motors.right_motor_pwm
left = motors.left_motor_pwm
right_dir = motors.right_motor_dir
left_dir = motors.left_motor_dir

assert left.freq() == 20833
assert right.freq() == 20833

motors.set_speeds(3000, 0)
assert left.duty_u16() == 32768, "left: 50% duty"
assert left_dir.value() == 0, "left fwd"
assert right.duty_u16() == 0, "right: 0% duty"
assert right_dir.value() == 0, "right fwd"

motors.set_speeds(6000, 3000)
assert left.duty_u16() == 65535, "left: 100% duty"
assert right.duty_u16() == 32768, "right: 50% duty"

motors.set_speeds(-6000, -3000)
assert left.duty_u16() == 65535, "left: -100% duty"
assert left_dir.value() == 1, "left bk"
assert right.duty_u16() == 32768, "right: -50% duty"
assert left_dir.value() == 1, "right bk"

motors.flip_left(True)
motors.set_speeds(-1, -1) # so it will really be 1, -1
assert left_dir.value() == 0, "left fwd 2"
assert right_dir.value() == 1, "right bk 2"

motors.flip_left(False)
motors.flip_right(True)
motors.set_speeds(1, 1) # so it will really be 1, -1
assert left.duty_u16() == 11, "left: min duty"
assert left_dir.value() == 0, "left fwd 3"
assert right.duty_u16() == 11, "right: min duty"
assert right_dir.value() == 1, "right bk 3"

motors.set_speeds(0, 0)
assert left_dir.value() == 0, "left: do not change dir on zero"
assert right_dir.value() == 1, "right: do not change dir on zero"

motors.set_left_speed(600)
assert left.duty_u16() == 6554, "left: single motor"
assert right.duty_u16() == 0, "right: still off"