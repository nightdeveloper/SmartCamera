#!/usr/bin/python
import math
import sys
import time

import Adafruit_GPIO.PCA9685 as PCA9685

print("Initializing PTZ controller...")

PWM_FREQ = 50.0  # from sg90/mgs90s docs


class Servo(object):

    def __init__(self, addr, start_impulse_ms, end_impulse_ms):
        self._addr = addr
        one_step = 1 / PWM_FREQ / float(PCA9685.PCA9685_BIT)
        self.servo_min = int(math.floor(float(start_impulse_ms) / 1000 / one_step))
        self.servo_max = int(math.floor(float(end_impulse_ms) / 1000 / one_step))
        self.servo_center = int(math.floor((self.servo_max + self.servo_min) / 2))
        self.addr = addr

        print("servo " + str(self.addr) + " init:  " +
              "min = " + str(self.servo_min) + ", " +
              "cemter = " + str(self.servo_center) + ", " +
              "max = " + str(self.servo_max))

    def move(self, position):
        if position < self.servo_min or position > self.servo_max:
            print("servo " + str(self.addr) + " out of range position: " + str(position))
        else:
            print("servo " + str(self.addr) + " moving to " + str(position))
            pwm.set_pwm(self.addr, 0, position)
            time.sleep(0.1)

    def center(self):
        self.move(self.servo_center)


try:
    pwm = PCA9685.PCA9685()

    pwm.set_pwm_freq(PWM_FREQ)

    h_servo = Servo(1, 1, 2)  # sg90,  hw address 1, duty 1-2ms
    v_servo = Servo(0, 1, 2)  # mg90s, hw address 0, duty 1-2ms

    for i in range(h_servo.servo_min, h_servo.servo_max, 10):
        h_servo.move(i)

    h_servo.center()

    for i in range(v_servo.servo_min, v_servo.servo_max, 10):
        v_servo.move(i)

    v_servo.center()

except():
    print(sys.exc_info()[0])

print("Exiting...")
