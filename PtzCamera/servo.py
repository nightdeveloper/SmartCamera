#!/usr/bin/python3
import math
import time
import logging
import PCA9685

PWM_FREQ = 50.0  # from sg90/mgs90s docs
MOVEMENT_DELAY = 0.3


class Servo(object):

    movement_delay = 0

    def __init__(self, addr, start_impulse_ms, end_impulse_ms, emulation = False):

        self.emulation = emulation

        if self.emulation is False:
            self.pwm = PCA9685.PCA9685()
            self.pwm.set_pwm_freq(PWM_FREQ)

        self._addr = addr
        one_step = 1 / PWM_FREQ / float(PCA9685.PCA9685_BIT)
        self.servo_min = int(math.floor(float(start_impulse_ms) / 1000 / one_step))
        self.servo_max = int(math.floor(float(end_impulse_ms) / 1000 / one_step))
        self.servo_center = int(math.floor((self.servo_max + self.servo_min) / 2))
        self.addr = addr

        logging.info("servo " + str(self.addr) + " init:  " +
                     "min = " + str(self.servo_min) + ", " +
                     "center = " + str(self.servo_center) + ", " +
                     "max = " + str(self.servo_max))

    def set_movement_delay(self, delay_time):
        logging.info("set movement delay " + str(delay_time))
        self.movement_delay = delay_time

    def move(self, position):
        if position < self.servo_min or position > self.servo_max:
            logging.info("servo " + str(self.addr) + " out of range position: " + str(position))
        else:
            logging.info("servo " + str(self.addr) + " moving to " + str(position))
            if self.emulation is False:
                self.pwm.set_pwm(self.addr, 0, position)
            time.sleep(0.05 + self.movement_delay)

    def center(self):
        self.move(self.servo_center)

    def min(self):
        self.move(self.servo_min)

    def max(self):
        self.move(self.servo_max)
