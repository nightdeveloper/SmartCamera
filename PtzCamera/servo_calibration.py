#!/usr/bin/python3
import sys

from servo import Servo

print("Initializing PTZ controller...")

try:
    h_servo = Servo(1, 0.7, 2.3)  # sg90,  hw address 1, duty 1-2ms
    v_servo = Servo(0, 0.7, 2.3)  # mg90s, hw address 0, duty 1-2ms

    for i in range(h_servo.servo_min, h_servo.servo_max, 1):
        h_servo.move(i)

    h_servo.center()

    for i in range(v_servo.servo_min, v_servo.servo_max, 1):
        v_servo.move(i)

    v_servo.center()

except():
    print(sys.exc_info()[0])

print("Exiting...")
