# accelerometro.py
# Lettura dati da sensore accelerometro ADXL345 via I2C

import board
import busio
import adafruit_adxl34x


class AccelerometroReader:

    # istanziati i2c e sensore
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.accel = adafruit_adxl34x.ADXL345(i2c)
        self.offset = (0.0, 0.0, 0.0)

    # Esegue una lettura singola, viene rilevato l'errore di misurazioni e salvato come offset
    def calibra(self):
        x, y, z = self.accel.acceleration
        self.offset = (x, y, z)
        print(f"[Accelerometro] Calibrato con offset: X={x:.2f} Y={y:.2f} Z={z:.2f}")

    # Ritorna la lettura dell'accelerometro con l'offset sottratto
    # se c'è un errore ritorna None
    def leggi(self):
        try:
            x, y, z = self.accel.acceleration
            ox, oy, oz = self.offset
            return round(x - ox, 2), round(y - oy, 2), round(z - oz, 2)
        except Exception as e:
            print(f"[Accelerometro] ERRORE: {e}")
            return None, None, None



#----------------------------------------------------------------------------------------

# Questa è una versione alternativa per gestire la calibrazione
# non c'è stato il tempo per testarla a dovere

'''

# accelerometro.py

import board
import busio
import time
import adafruit_adxl34x

class AccelerometroReader:
    def init(self):
        # Inizializzazione I2C e sensore
        i2c = busio.I2C(board.SCL, board.SDA)
        self.accel = adafruit_adxl34x.ADXL345(i2c)
        self.offset = (0.0, 0.0, 0.0)

    def calibra(self, campioni=100, attesa=0.01):
        """Calcola la media su più letture per compensare l'offset"""
        print("[Accelerometro] Avvio calibrazione...")

        somma_x, somma_y, somma_z = 0.0, 0.0, 0.0
        for _ in range(campioni):
            x, y, z = self.accel.acceleration
            somma_x += x
            somma_y += y
            somma_z += z
            time.sleep(attesa)

        self.offset = (
            somma_x / campioni,
            somma_y / campioni,
            somma_z / campioni - 9.81  # corregge la gravità sulla Z
        )

        ox, oy, oz = self.offset
        print(f"[Accelerometro] Offset calcolato: X={ox:.2f} Y={oy:.2f} Z={oz:.2f}")

    def leggi(self):
        try:
            x, y, z = self.accel.acceleration
            ox, oy, oz = self.offset
            return round(x - ox, 2), round(y - oy, 2), round(z - oz, 2)
        except Exception as e:
            print(f"[Accelerometro] ERRORE: {e}")
            return None, None, None

'''


