import RPi.GPIO as GPIO
import time
import pygame




GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(27,GPIO.IN)

p = GPIO.PWM(18, 50)
p.start(5.5)
p.stop()
time.sleep(1)

pygame.init()
pygame.mixer.music.load("sounds/intro.wav")
pygame.mixer.music.play()

try:
    while True:
        print(GPIO.input(27))
        p.ChangeDutyCycle(5.5)
        time.sleep(0.1)
        p.ChangeDutyCycle(5)
        time.sleep(0.1)
except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()
