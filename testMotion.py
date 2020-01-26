import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.IN)



try:
    while True:
        i = GPIO.input(18)
        if i==1:
            print("INTRUDER")
        else:
            print("SAFE")
        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("finish")
    GPIO.cleanup()