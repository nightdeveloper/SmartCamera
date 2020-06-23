#!/usr/bin/python3
import time
from PtzCamera.TSL2581 import TSL2581

try:
    Light = TSL2581(0X39, debug=False)

    light_id = Light.Read_ID() & 0xf0
    print('ID = {0}'.format(light_id))
    Light.Init_TSL2581()
    
    while True:
        lux = Light.calculate_Lux()
        print("lux = ", lux)
        time.sleep(1)

except Exception as e:
    # GPIO.cleanup()
    print("\nProgram end {0}".format(e))
    exit()