# sensore_ultrasuoni.py
# Classe per gestire un sensore a ultrasuoni

import RPi.GPIO as GPIO
import time


class SensoreUltrasuoni:

    # Inizializza il sensore con i pin trigger ed echo
    def init(self, trigger_pin, echo_pin):
        self.trigger = trigger_pin
        self.echo = echo_pin
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, GPIO.LOW)
        time.sleep(0.1)

    # Ritorna la distanza misurata in cm
    def misura_distanza_cm(self):

        # Invia impulso di 10 microsecondi
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)

        # Attendi inizio impulso echo
        start_time = time.time()
        timeout = start_time + 0.04 # per rumore continuo
        while GPIO.input(self.echo) == 0 and time.time() < timeout:
            start_time = time.time()

        # Attendi fine impulso echo e lo salva in stop_time
        stop_time = time.time()
        timeout = stop_time + 0.04
        while GPIO.input(self.echo) == 1 and time.time() < timeout:
            stop_time = time.time()

        # Durata dell'impulso * velocità del suono (34300 cm/s) / 2 (andata e ritorno)
        durata = stop_time - start_time
        distanza = (durata * 34300) / 2  # cm

        return round(distanza, 1)