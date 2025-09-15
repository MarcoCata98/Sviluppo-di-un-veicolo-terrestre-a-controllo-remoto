#visualizzaDati.py
# vengono generati grafici in tempo reale con i dati letti da InfluxDB

# !! questo modulo può venir sostituito da Grafana, che è esteticamente migliore e più efficiente !!

import pygame
import sys
import time
import statistics
from influxdb_client import InfluxDBClient

# === Config InfluxDB ===
URL = "http://localhost:8086"
TOKEN = "9-6z3SNN0R3X5H5nxjwda0DqShJXyCC9VQrfSVayP63NCTh7CA0SSetamkFNhlPXl3jv-uk7w3jONgK1fX9zXw=="
ORG = "RCAR"
BUCKET = "CarSensors"

client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
query_api = client.query_api()


# -----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

# === Pygame ===


pygame.init()
LARG, ALT = 900, 600
screen = pygame.display.set_mode((LARG, ALT))
pygame.display.set_caption("Telemetria RC Car")
FONT = pygame.font.SysFont("consolas", 18)
BIANCO, NERO, ROSSO, VERDE, GIALLO, GRIGIO = (255,255,255), (0,0,0), (200,0,0), (0,200,0), (255,255,0), (50,50,50)

andamento_volt = []
MAX_VOLT = 8.0
MIN_VOLT = 6.5


def disegna_batteria(schermo, x, y, percentuale, med_volt):
    pygame.draw.rect(schermo, NERO, (x, y, 120, 50), 3)
    pygame.draw.rect(schermo, NERO, (x+120, y+15, 10, 20))
    lung = max(0, min(int(1.2 * percentuale), 120))
    colore = VERDE if percentuale > 40 else GIALLO if percentuale > 25 else ROSSO
    pygame.draw.rect(schermo, colore, (x+2, y+2, lung, 46))
    txt = FONT.render(f"{int(percentuale)}%", True, BIANCO)
    volt_txt = FONT.render(f"{med_volt:.2f}V", True, BIANCO)
    schermo.blit(txt, (x+35, y+10))
    schermo.blit(volt_txt, (x+30, y+30))

def disegna_grafico_volt(schermo, x, y, w, h, dati):
    pygame.draw.rect(schermo, NERO, (x, y, w, h), 2)
    if len(dati) < 2:
        return

    punti = []
    max_len = len(dati)
    for i, v in enumerate(dati):
        px = x + i * (w // max_len)
        py = y + h - int((v - MIN_VOLT) / (MAX_VOLT - MIN_VOLT) * h)
        py = max(y, min(y + h, py))  # Clamp
        punti.append((px, py))
    pygame.draw.lines(schermo, VERDE, False, punti, 2)

    # Disegna etichette assi
    for i in range(0, max_len, max_len // 5 if max_len >= 5 else 1):
        minute_label = FONT.render(f"-{max_len - i}s", True, BIANCO)
        screen.blit(minute_label, (x + i * (w // max_len), y + h + 5))
    for v in range(int(MIN_VOLT*10), int(MAX_VOLT*10), 10):
        v /= 10
        py = y + h - int((v - MIN_VOLT) / (MAX_VOLT - MIN_VOLT) * h)
        volt_label = FONT.render(f"{v:.1f}", True, BIANCO)
        screen.blit(volt_label, (x - 40, py - 10))

def disegna_ultrasuoni(schermo, x, y, valori):
    pygame.draw.rect(schermo, NERO, (x, y, 250, 180), 2)
    centro = (x + 125, y + 130)
    pygame.draw.polygon(schermo, BIANCO, [(centro[0], centro[1]-30), (centro[0]-20, centro[1]+20), (centro[0]+20, centro[1]+20)])
    posizioni = {
        "davanti": (centro[0], centro[1]-80),
        "sinistra": (centro[0]-80, centro[1]),
        "destra": (centro[0]+80, centro[1])
    }
    for direzione, valore in valori.items():
        if valore is None: continue
        colore = VERDE if valore > 35 else GIALLO if valore > 25 else ROSSO
        pygame.draw.circle(schermo, colore, posizioni[direzione], 10)
        txt = FONT.render(f"{int(valore)}cm", True, BIANCO)
        schermo.blit(txt, (posizioni[direzione][0]-20, posizioni[direzione][1]-30))

def disegna_accelerometro(schermo, x, y, accx, accy):
    pygame.draw.rect(schermo, NERO, (x, y, 250, 180), 2)
    centro = (x + 125, y + 90)
    pygame.draw.polygon(schermo, BIANCO, [(centro[0], centro[1]-30), (centro[0]-20, centro[1]+20), (centro[0]+20, centro[1]+20)])
    soglia = 0.3
    if abs(accy) > soglia:
        freccia = [(centro[0], centro[1]-60), (centro[0]-10, centro[1]-40), (centro[0]+10, centro[1]-40)] if accy > 0 else [(centro[0], centro[1]+60), (centro[0]-10, centro[1]+40), (centro[0]+10, centro[1]+40)]
        pygame.draw.polygon(schermo, GIALLO, freccia)
    if abs(accx) > soglia:
        freccia = [(centro[0]-60, centro[1]), (centro[0]-40, centro[1]-10), (centro[0]-40, centro[1]+10)] if accx > 0 else [(centro[0]+60, centro[1]), (centro[0]+40, centro[1]-10), (centro[0]+40, centro[1]+10)]
        pygame.draw.polygon(schermo, GIALLO, freccia)



#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------


# FUNZIONI DI ESTRAZIONE DEI DATI

# Funzioni lettura ultimo valore di un sensore (identica a leggiDati.py) 
def leggi_ultimo_valore(meas, field):
    query = f'''from(bucket: "{BUCKET}") |> range(start: -1m) |> filter(fn: (r) => r._measurement == "{meas}") |> filter(fn: (r) => r._field == "{field}") |> last()'''
    result = query_api.query(query)
    for t in result:
        for r in t.records:
            return r.get_value()
    return None


# Funzione lettura ultimi n valori di un sensore
# MI SERVE PER IL GRAFICO DELLA TENSIONE BATTERIA
def leggi_valori(meas, field, n=30):
    query = f'''from(bucket: "{BUCKET}") |> range(start: -1m) |> filter(fn: (r) => r._measurement == "{meas}") |> filter(fn: (r) => r._field == "{field}") |> sort(columns: ["_time"], desc: true) |> limit(n:{n})'''
    result = query_api.query(query)
    return [r.get_value() for t in result for r in t.records]


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------


# === Main Loop ===
clock = pygame.time.Clock()
volt_history = [] # storia degli "ultimi valori" della tensione, vengono memorizzati per fare il grafico a linee

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(GRIGIO)

    # ------------------------

    # === Lettura dati ===
    volt = leggi_ultimo_valore("volt_batteria_principale", "volt")
    volt_vals = leggi_valori("volt_batteria_principale", "volt", 30) # estraggo gli ultimi 30 valori

    # memorizzare gli ultimi valori letti per il grafico
    if volt: 
        volt_history.append(volt)

    # tolgo i più vecchi se supero 50
    if len(volt_history) > 50:
        volt_history.pop(0)

    # mediana valori e percentuale batteria
    # !! NEL GRAFICO A FORMA DI BATTERIA, PER AVERE UN VALORE STABILE, USO LA MEDIANA DEGLI ULTIMI 30 VALORI
    med_volt = statistics.median(volt_vals) if volt_vals else 0
    percentuale = int(100 * (med_volt - MIN_VOLT) / (MAX_VOLT - MIN_VOLT)) if volt_vals else 0

    # valori sensori ultrasuoni
    us_vals = {
        "davanti": leggi_ultimo_valore("distanza_ultrasuoni", "distanza_davanti"),
        "destra": leggi_ultimo_valore("distanza_ultrasuoni", "distanza_dx"),
        "sinistra": leggi_ultimo_valore("distanza_ultrasuoni", "distanza_sx")
    }

    # valori accelerometro
    accx = leggi_ultimo_valore("acc", "acc_x") or 0
    accy = leggi_ultimo_valore("acc", "acc_y") or 0


    # Disegno grafici in base ai valori misurati
    disegna_grafico_volt(screen, 60, 20, 800, 100, volt_history)
    disegna_batteria(screen, 50, 140, percentuale, med_volt)
    disegna_ultrasuoni(screen, 50, 220, us_vals)
    disegna_accelerometro(screen, 330, 220, accx, accy)

    pygame.display.flip()
    clock.tick(2)
