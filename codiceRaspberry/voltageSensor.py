# voltage_reader.py
# Legge il voltaggio del partitore di tensione collegato alla batteria
# Usa il convertitore analogico-digitale ADS1115 collegato via I2C per leggere il segnale analogico
# e ricava il valore reale


import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

DIVIDER_RATIO = 5.0  # (R1 + R2) / R2  resistenze da 100kOhm e 25kOhm

class VoltageReader:
    def __init__(self):
        
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)
        self.chan = AnalogIn(self.ads, ADS.P0)


    # Legge il voltaggio della batteria, che gli arriva tramite segnale analogico dal partitore di tensione
    # il ripartitore ritorna il valore diviso per il 5

    # quindi il valore letto va moltiplicato per 5 per ottenere quello reale
    def leggi_batteria(self):
        return self.chan.voltage * DIVIDER_RATIO
