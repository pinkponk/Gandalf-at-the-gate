#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

import re
import time
import argparse

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

import pygame
import speech_recognition as sr
import RPi.GPIO as GPIO
import time
import random

centerDuty = 5.0
maxDeltaDuty = 0.6




def waitForGuest():
    while True:
        i = GPIO.input(27)
        if i==1:
            print("GUEST")
            return
        else:
            print("no one here")
        time.sleep(0.5)

def setupServo():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27,GPIO.IN)
    GPIO.setup(18,GPIO.OUT)

    p = GPIO.PWM(18, 50)
    p.start(5.0)
    #time.sleep(1)
    p.ChangeDutyCycle(0)
    return p

def moveServo_random_pos(p):
    #pos = random.random()*maxDeltaDuty+centerDuty
    pos = random.choice([5.2,4.8])
    #print("pos=",pos)
    p.ChangeDutyCycle(pos)
    



def drawEyeBalls(draw, x,y,squint=False):

    
    x0 = x-2
    y0 = y-2
    x1 = x+2
    y1 = y+2
    

    if squint:
        y1-=1
    
    draw.ellipse([x0,y0,x1,y1], fill=1, outline=1)
    
    x0=x0+8
    x1=x1+8
    draw.ellipse([x0,y0,x1,y1], fill=1, outline=1)


def drawEyeBrow(draw, mode, isRightEye):

    x0 = 0
    y0 = 0
    x1 = 7
    y1 = 1
        
    if isRightEye:
        x0=15-x0
        x1=15-x1
        
    if mode==0:
        draw.line([x0,y0,x1,y1],fill=1)
    elif mode==1:
        y1-=1
        draw.line([x0,y0,x1,y1],fill=1)
    elif mode==-1:
        y1+=1
        draw.line([x0,y0,x1,y1],fill=1)
    
    
def test(device):
    device.contrast(100)
    
    #Eye brows up and down
    for i in [0,1,0,1,0,1,0,1,0]:
        with canvas(device) as draw:
            drawEyeBalls(draw,4,4,squint=False)
            drawEyeBrow(draw, i, isRightEye=False)
            drawEyeBrow(draw, i, isRightEye=True)
            time.sleep(0.3)
    
    
    time.sleep(1)
    
    
        
    #Eye round
    for i in range(3):
        for (x,y) in zip([5,5,4,3,3,3,4,5],[4,5,5,5,4,3,3,3,4]):
            with canvas(device) as draw:
                drawEyeBalls(draw,x,y,squint=False)
                drawEyeBrow(draw, 0, isRightEye=False)
                drawEyeBrow(draw, 0, isRightEye=True)
                time.sleep(0.1)
    
    
    
    #Left center left center
    for i in range(2):
        with canvas(device) as draw:
            drawEyeBalls(draw,3,5,squint=False)
            drawEyeBrow(draw, -1, isRightEye=False)
            drawEyeBrow(draw, -1, isRightEye=True)
            time.sleep(0.3)
            
        with canvas(device) as draw:
            drawEyeBalls(draw,3,5,squint=False)
            drawEyeBrow(draw, 0, isRightEye=False)
            drawEyeBrow(draw, 0, isRightEye=True)
            time.sleep(0.3)
            
            
            

def moveEyes_random(device, eyeX, eyeY, squint, brow1, brow2):
    #Left center left center
    randomFeature = random.choice(["eyeX","eyeY","brow1","brow2","squint"])


    if randomFeature == "eyeX":
        eyeX = random.choice([2,3,3,3,4])
    elif randomFeature == "eyeY":
        eyeY = random.choice([4,5,5,5,6])
    elif randomFeature == "brow1":
        brow1 = random.choice([-1,0,0,0,1])
    elif randomFeature == "brow2":
        brow2 = random.choice([-1,0,0,0,1])
    elif randomFeature == "squint":
        squint = random.choice([True,False,False])


    with canvas(device) as draw:
        drawEyeBalls(draw,eyeX,eyeY,squint=squint)
        drawEyeBrow(draw, brow1, isRightEye=False)
        drawEyeBrow(draw, brow2, isRightEye=True)
    return eyeX, eyeY, squint, brow1, brow2

    
def demo(n, block_orientation, rotate):
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation, rotate=rotate or 0)
    print("Created device")

    
    pygame.init()
    pygame.mixer.music.load("durin.wav")
    pygame.mixer.music.play()


    #time.sleep(1)
    
 


    test(device)
    
    #device.contrast(100)
    #with canvas(device) as draw:
        #draw.ellipse([2,2,6,6], fill=1, outline=1)
     #   drawEyeBalls(draw, x=3,y=5,squint=True)
      #  drawEyeBrow(draw, -1, False)
       # drawEyeBrow(draw, -1, True)
        #draw.line([0,7,8,7],fill=0)
        #draw.rectangle(device.bounding_box, outline="white", fill="black")

    #time.sleep(1)
    #for x in range(256):
    #    with canvas(device) as draw:
    #        text(draw, (0, 0), chr(x), fill="white")
    #        time.sleep(0.1)

def analyseAnswer(audio, r):
    
    try:
        answer = r.recognize_google(audio)
        return answer, True
    except sr.RequestError:
        print("API unavailable")
        return None, False
    except sr.UnknownValueError:
        print("Unable to recognize speech")
        return None, False
    

def listenForAnswer(source, r):
    try:
        audio = r.listen(source, timeout=10, phrase_time_limit=3)
        return audio, True
    except sr.WaitTimeoutError:
        print("You took to long")
        return None, False


def gandalfAtTheGate(p, device):
    device.contrast(50)
    r = sr.Recognizer()

    mic = sr.Microphone()

    #print(sr.Microphone.list_microphone_names())
    #p.stop()
    
    with mic as source:
        print("Adjusting..")
        r.adjust_for_ambient_noise(source)
        print("Adjusting")
        
        while True:
            time.sleep(10)
            waitForGuest()
            
            print("Guest arrived!")
                  
            eyeX = 3
            eyeY = 5
            squint = False
            brow1 = 0
            brow2 = 0

            
 
            
            ##### Play welcome speech and riddle
            #----
            pygame.init()
            
            pygame.mixer.music.load("sounds/intro.wav")
            pygame.mixer.music.play()
            #p.start(5.0)
            while pygame.mixer.music.get_busy() == True:
                moveServo_random_pos(p)
                eyeX, eyeY, squint, brow1, brow2 = moveEyes_random(device, eyeX, eyeY, squint, brow1, brow2)
                time.sleep(0.2)
            time.sleep(0.5)
            
            
            riddle = random.choice(["map","fire","darkness"])
            
            pygame.mixer.music.load("sounds/"+riddle+".wav")
            pygame.mixer.music.play()
            #p.start(5.0)
            while pygame.mixer.music.get_busy() == True:
                #moveServo_random_pos(p)
                time.sleep(0.1)
            #p.stop()
            p.ChangeDutyCycle(0)
            #Listen for answer
            audio, sucess = listenForAnswer(source, r)
            
            correct = False
            if sucess:
                answer, sucess2 = analyseAnswer(audio, r)
                #answer = "fee"
                #sucess2 = True

                print(answer)
                if sucess2:
                    if riddle in answer.lower():
                        correct = True
                else:
                    print("could not understand you")
            else:
                print("could not here you")
                
            #Respond
            if correct:
                pygame.mixer.music.load("sounds/correct.wav")
                pygame.mixer.music.play()
                #p.start(5.0)
                while pygame.mixer.music.get_busy() == True:
                    moveServo_random_pos(p)
                    time.sleep(0.1)
                p.ChangeDutyCycle(0)
            else:
                #p.start(5.0)
                pygame.mixer.music.load("sounds/incorrect.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    moveServo_random_pos(p)
                    time.sleep(0.1)
                pygame.mixer.music.load("sounds/shallnotpass.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    moveServo_random_pos(p)
                    time.sleep(0.1)
                pygame.mixer.music.load("sounds/doasyourwish.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    moveServo_random_pos(p)
                    time.sleep(0.1)
                p.ChangeDutyCycle(0)
            print("DONE")
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='matrix_demo arguments',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--cascaded', '-n', type=int, default=2, help='Number of cascaded MAX7219 LED matrices')
    parser.add_argument('--block-orientation', type=int, default=90, choices=[0, 90, -90], help='Corrects block orientation when wired vertically')
    parser.add_argument('--rotate', type=int, default=0, choices=[0, 1, 2, 3], help='Rotate display 0=0°, 1=90°, 2=180°, 3=270°')
    args = parser.parse_args()
    #GPIO.cleanup()
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=args.cascaded or 1, block_orientation=args.block_orientation, rotate=args.rotate or 0)
    print("Created device")

    p = setupServo()
    #p.start(5.0)
    #p.stop()
    # p=0
    try:
       gandalfAtTheGate(p,device)
    except KeyboardInterrupt:
        pass
    #p.stop()
    GPIO.cleanup()
