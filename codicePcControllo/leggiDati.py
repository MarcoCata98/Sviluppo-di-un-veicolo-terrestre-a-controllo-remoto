# leggiDati.py
# Legge i dati più recenti da InfluxDB e li stampa in console

from influxdb_client import InfluxDBClient
import time


# CONFIGURAZIONE INFLUXDB

URL = "http://localhost:8086"
TOKEN = "9-6z3SNN0R3X5H5nxjwda0DqShJXyCC9VQrfSVayP63NCTh7CA0SSetamkFNhlPXl3jv-uk7w3jONgK1fX9zXw=="
ORG = "RCAR"
BUCKET = "CarSensors"


client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
query_api = client.query_api()


# ------------------------------------------------------------------------------


# Lista dei sensori: (measurement, field, descrizione)
SENSORI = [
    ("volt_batteria_principale", "volt", " Batteria principale "),
    ("distanza_ultrasuoni", "distanza_davanti", " Ultrasuoni davanti "),
    ("distanza_ultrasuoni", "distanza_dx", " Ultrasuoni destra "),
    ("distanza_ultrasuoni", "distanza_sx", " Ultrasuoni sinistra "),
    ("acc", "acc_x", " Accelerazione X "),
    ("acc", "acc_y", " Accelerazione Y "),
    ("acc", "acc_z", " Accelerazione Z "),
]


# costruisce la query per leggere l'ultimo valore di (measurement, field)
def leggi_ultimo_valore(measurement, field):
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -1m)
      |> filter(fn: (r) => r._measurement == "{measurement}")
      |> filter(fn: (r) => r._field == "{field}")
      |> last()
    '''

    # la query ritorna la lista di tabelle, con una tabella, contenente un record (l'utltimo valore)
    tables = query_api.query(query)   
    for table in tables:
        for record in table.records:
            return record.get_value()
    return None  

# ---------------------------------------------------------------------

#  Main loop


# vengono estratti gli ultimi valori di tutti i sensori e stampati in console
def avvia_lettura():
    while True:
        print("────── Ultimi valori sensori ──────")
        for measurement, field, descrizione in SENSORI:
            valore = leggi_ultimo_valore(measurement, field)
            if valore is not None:
                print(f"{descrizione}: {valore:.2f}")
            else:
                print(f"{descrizione}: Nessun dato")
        print("──────────────────────────────────────\n")
        time.sleep(0.5)



# eseguito su un terminale separato

if __name__ == "__main__":
    avvia_lettura()