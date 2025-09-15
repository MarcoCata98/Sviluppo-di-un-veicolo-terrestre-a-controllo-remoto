# buzzer.py
# comandi per accendere e spegnere il buzzer

import RPi.GPIO as GPIO
import time
import threading

class Buzzer:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def accendi(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def spegni(self):
        GPIO.output(self.pin, GPIO.LOW)
