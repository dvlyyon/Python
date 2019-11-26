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
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)
        is_close = True
        while True:
                temp = cpu_temp()
                if is_close:
                        if temp > 68.0:
                                print("current temperature: " + str(temp))
                                print(time.ctime() + " : " + str(temp) + " -> open air fan")
                                GPIO.output(channel, GPIO.LOW)
                                is_close = False
                else:
                        if temp < 50.0:
                                print("current temperature: " + str(temp))
                                print(time.ctime() + " : " + str(temp) + " -> close air fan")
                                GPIO.output(channel, GPIO.HIGH)
                                is_close = True
                time.sleep(5.0)

if __name__ == '__main__':
        main()  


