# ManagerDati.py
# Gestisce i dati ricevuti dai sensori via MQTT e li salva su InfluxDB

# Questo script viene eseguito su un terminale, quindi tutti i print() saranno visibili

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import time


#-----------------------------------------------------------------------------------

# GESTIONE INFLUXDB

# === CONFIGURAZIONE INFLUXDB ===
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "9-6z3SNN0R3X5H5nxjwda0DqShJXyCC9VQrfSVayP63NCTh7CA0SSetamkFNhlPXl3jv-uk7w3jONgK1fX9zXw=="
INFLUXDB_ORG = "RCAR"
INFLUXDB_BUCKET = "CarSensors"

client_influx = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client_influx.write_api(write_options=SYNCHRONOUS)



# === Invio dati a InfluxDB ===

# Invia il dato al database InfluxDB
    # measurement: nome della misura (es. "volt_batteria_principale")
    # field: nome del campo (es. "volt")
    # value: valore del campo (es. 12.5)
    # timestamp: opzionale, se non fornito usa il tempo attuale in nanosecondi
def inviaDatoDB(measurement, field, value, timestamp=None):

    # calcola timestamp in nanosecondi
    if timestamp is None:
        timestamp = int(time.time_ns()) 

    # crea il point (metodo di conservazione dati di InfluxDB)
    point = Point(measurement).field(field, value).time(timestamp)

    print("caricato: " + point.to_line_protocol()) #scrive <mesurament> <field> <value> <timestamp>
   
    # invia al database
    try:
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    except Exception as e:
        print(f"[Errore Influxdb ] Errore invio al DB: {e}")


#-----------------------------------------------------------------------------------


# === GESTIONE MESSAGGI MQTT ===

IP_MOSQUITTO = "localhost"  # indirizzo del broker MQTT (sta girando sul pc di controllo)
PORTA_MOSQUITTO = 1883      # porta del broker MQTT (default 1883)

'''
    ManagerDati è un client MQTT che legge i messaggi dal server/broker Mosquitto
    Mosquitto è un altro processo sullo stesso dispositivo (localhost)               -- si collegano localmente
    e Mosquitto è collegato anche al server raspberry che sarà un altro client MQTT  -- si collegano da remoto

'''


# tra ManagerDati e Mosquitto
# e io ManagerDati mi iscrivo al canale sensori/#
# quindi quando Mosquitto riceve un messaggio sul quel canale, verrò avvisato anche io
# e chiamerò in auto la funzione on_message() che leggerà il dato, e potrò manipolarlo
def connessione_mqtt():
    client = mqtt.Client()
    client.on_message = on_message

    client.connect(IP_MOSQUITTO, PORTA_MOSQUITTO, 60)  #ogni 60 secondi manda un ping al server per rimanere connesso
    client.subscribe("sensori/#")

    print("[ManagerDati] Connessione MQTT stabilita. In ascolto su 'sensori/#'...")
    client.loop_forever()  # rimane in ascolto per sempre





# chiamata ogni volta che arriva un messaggio MQTT a mosquitto
# sul canale sensori/# = quindi a ManagerDati arrivano tutti i dati di tutti i sensori
def on_message(client, userdata, msg):

# ricevo un messaggio
    try:
        topic = msg.topic                   # topic = canale completo su cui è arrivato il messaggio (es. "sensori/voltaggio")
        payload = msg.payload.decode()      # payload = contenuto del messaggio (es. "12.5")


        # GESTIRO' OGNI SENSORE CON IL SUO TOPIC SPECIFICO
        # e lo salverò nel database InfluxDB con un proprio field e measurement

        if topic == "sensori/voltaggio":
            valore = float(payload)  
            inviaDatoDB("volt_batteria_principale", "volt", valore)
       
        elif topic == "sensori/ultrasuoni/davanti":
            valore = float(payload)
            inviaDatoDB("distanza_ultrasuoni", "distanza_davanti", valore)

        elif topic == "sensori/ultrasuoni/dx":
            valore = float(payload)
            inviaDatoDB("distanza_ultrasuoni", "distanza_dx", valore)

        elif topic == "sensori/ultrasuoni/sx":
            valore = float(payload)
            inviaDatoDB("distanza_ultrasuoni", "distanza_sx", valore)

        elif topic == "sensori/accelerometro/x":
            valore = float(payload)
            inviaDatoDB("acc", "acc_x", valore)

        elif topic == "sensori/accelerometro/y":
            valore = float(payload)
            inviaDatoDB("acc", "acc_y", valore)

        elif topic == "sensori/accelerometro/z":
            valore = float(payload)
            inviaDatoDB("acc", "acc_z", valore)
        
       
       
       
        else:
            print(f"[Errore MQTT] Topic non gestito: {topic} → {payload}") 

    except Exception as e:
        print(f"[Errore MQTT] Errore nella gestione messaggio: {e}")


#-----------------------------------------------------------------------------------

# Main
# Viene eseguito in un terminale esterno
# in modo da monitorare tutti i messaggi di log

if __name__ == "__main__":
    connessione_mqtt()