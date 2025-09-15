# motori.py
# lista di funzioni che gestiscono i motori di sterzo e trazione


import RPi.GPIO as GPIO
import time

# Pin motore sterzo (motore A)
ENA = 18
IN1 = 23
IN2 = 24

# Pin motore trazione (motore B)
ENB = 19
IN3 = 5
IN4 = 6

#------------------------------------------------------

pwmA = None
pwmB = None

# imposta i pin e avvia i motori
def avviaMotore():
    global pwmA, pwmB
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB], GPIO.OUT)
    
    pwmA = GPIO.PWM(ENA, 1000)  
    pwmB = GPIO.PWM(ENB, 1000)

    pwmA.start(0)
    pwmB.start(0)


# stop totale dei motori, sia sterzo che trazione
def fermo():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)


# grazie al PONTE H, basta invertire la corrente ai pin per cambiare direzione

# accelera in avanti con tot potenza (in base al Duty Cycle)
def avanti(potenza=50):
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmB.ChangeDutyCycle(potenza)

# accelera in indietro con tot potenza (in base al Duty Cycle)
def indietro(potenza=50):
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwmB.ChangeDutyCycle(potenza)

# gira lo sterzo a destra con tot potenza (in base al Duty Cycle)
def destra(potenza=50):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwmA.ChangeDutyCycle(potenza)

# gira lo sterzo a sinistra con tot potenza (in base al Duty Cycle)
def sinistra(potenza=50):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(potenza)

# spegne i motori e pulisce i pin GPIO
def spegniMotore():
    fermo()
    pwmA.stop()
    pwmB.stop()
    GPIO.cleanup()

# interrompo la corrente allo sterzo
def sterzo_a_zero():
    pwmA.ChangeDutyCycle(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

# interrompo la corrente alla trazione
def trazione_a_zero():
    pwmB.ChangeDutyCycle(0)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)


