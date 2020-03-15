#!/usr/bin/python3

import sys
import time

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! try to use sudo to run your script")

def cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
        return float(f.read())/1000

def main():
    channel = 16
    temp_high = 68
    temp_low  = 50
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)
    is_close = True
    while True:
        temp = cpu_temp()
        if is_close:
            if temp > temp_high:
                print("O",end='',flush=True)
                GPIO.output(channel, GPIO.LOW)
                is_close = False
            else:
                if temp < temp_low:
                    print(".",end='',flush=True)
                else:
                    print("o",end='',flush=True)
        else:
            if temp < temp_low:
                print(".",end='',flush=True)
                GPIO.output(channel, GPIO.HIGH)
                is_close = True
            else:
                if temp > temp_high:
                    print("O",end='',flush=True)
                else:
                    print("o",end='',flush=True)
        time.sleep(5.0)

if __name__ == '__main__':
    main()  


