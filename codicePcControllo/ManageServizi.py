# ManageServizi.py
# Funzioni per gestire i servizi InfluxDB e Mosquitto (avvio, chiusura, verifica stato)

'''
    le interfacce tornano (True/False, messaggio informativo da stampare nella console fittizia)
    true = successo, false = errore


    background = già esegue su un thread separato (non serve farlo nella GUI)

'''


import subprocess
import time
import os
import signal

PortaMosquitto = 1883
PortaInfluxDB = 8086

# file mosquitto con la configurazione globale (è locale di default)
# quindi quando scarichi mosquitto, modifica questo file e usalo come parametro per l'avvio
mosquitto_config_path = "/opt/homebrew/etc/mosquitto/mosquitto.conf"


#----------------------------------------------------------------------------


# INTERFACCIA INFLUXDB

# Interfaccia di controllo stato per InfluxDB
def verifica_influxdb():
    isAttivo, msg = _influxdb_is_attivo()
    return isAttivo, msg

# Interfaccia di chiusura per InfluxDB
def chiudi_influxdb():
    isAttivo, msg = verifica_influxdb()
    if not isAttivo:
        return False, "[Influxdb - errore] InfluxDB non è attivo. "
    return _chiudi_influxdb()

# Interfaccia di avvio per InfluxDB
def avvia_influxdb():
    isAttivo, msg = verifica_influxdb()
    if isAttivo:
        return False, "[Influxdb - errore] InfluxDB è già attivo. "
    return _avvia_influxdb()


# INTERFACCIA MOSQUITTO

# Interfaccia di controllo stato per Mosquitto
def verifica_mosquitto():
    isAttivo, msg = _mosquitto_is_attivo()
    return isAttivo, msg

# Interfaccia di chiusura per Mosquitto
def chiudi_mosquitto():
    isAttivo, msg = verifica_mosquitto()
    if not isAttivo:
        return False, "[Mosquitto - errore] Mosquitto non è attivo. "
    return _chiudi_mosquitto()

# Interfaccia di avvio per Mosquitto
def avvia_mosquitto():
    isAttivo, msg = verifica_mosquitto()
    if isAttivo:
        return False, "[Mosquitto - errore] Mosquitto è già attivo. "
    return _avvia_mosquitto()

# ----------------------------------------------------------------------------


# FUNZIONI PRIVATE INFLUXDB

## Controlla se InfluxDB è attivo
def _influxdb_is_attivo():
    try:
        # output = lista processi che ascoltano sulla porta 8086 (tipica di InfluxDB)
        result = subprocess.run(['lsof', '-i', f':{PortaInfluxDB}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        # se uno di questi è in stato di LISTEN = allora influxdb è attivo
        for riga in output.splitlines():
            if "LISTEN" in riga and (f":{PortaInfluxDB}" in riga):
                return True, f"[InfluxDB - info] InfluxDB è attivo sulla porta {PortaInfluxDB}."
            
        # altrimenti semplicemente non è attivo
        return False, f"[InfluxDB - info] InfluxDB non è attivo"
    
    except Exception as e:
        return False, f"[InfluxDB - errore] Errore durante la verifica di InfluxDB: {e}"



## Chiude InfluxDB terminando tutti i processi "influxd"
def _chiudi_influxdb():
    try:
        # pids = lista processi con nome "influxd"
        result = subprocess.run(['pgrep', '-f', 'influxd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pids = result.stdout.strip().split()

        # se non ci sono processi, restituisci un messaggio errore
        if not pids:
            return False, "[Influxdb - Errore] Nessun processo InfluxDB (influxd) trovato."
        
        # se ci sono, termina tutti i processi con nome "influxd"
        for pid in pids:
            os.kill(int(pid), signal.SIGTERM)
        return True, "[Influxdb - successo] InfluxDB terminato con successo."
    
    except Exception as e:
        return False, f"[Influxdb - errore] Errore durante la chiusura di InfluxDB: {e}"




## Avvia un processo InfluxDB in background
def _avvia_influxdb():
    try:
        # avvia un processo in background, con il comando 'influxd' 
        subprocess.Popen(['influxd'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(2)  # attende 2 secondi per dare il tempo a InfluxDB di avviarsi

        # verifica se si è attivato
        isAttivo, verifica_msg = _influxdb_is_attivo()
        if isAttivo:
            return True, "[InfluxDB - info] InfluxDB è stato avviato con successo. "
        else:
            return False, "[InfluxDB - errore] InfluxDB non si è avviato correttamente. "
        
    except Exception as e:
        return False, f"[InfluxDB - errore] Errore durante l'avvio di InfluxDB: {e}"


# ----------------------------------------------------------------------------


# FUNZIONI PRIVATE MOSQUITTO

## Controlla se Mosquitto è attivo
def _mosquitto_is_attivo():
    try:
        # output = lista processi che ascoltano sulla porta 1883 (tipica di Mosquitto)
        result = subprocess.run(['lsof', '-i', f':{PortaMosquitto}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        # se uno di questi è in stato di LISTEN
        for riga in output.splitlines():
            if "LISTEN" in riga:
                # ed ha la porta 1883 o ibm-mqisdp = allora mosquitto è perfettamente attivo 
                if f"*:{PortaMosquitto}" in riga or "*:ibm-mqisdp" in riga:
                    return True, f"[Mosquitto - info] Mosquitto è attivo sulla porta {PortaMosquitto}."
                # se ha scritto localhost: allora è in modalità only local, non va bene
                elif "localhost:" in riga:
                    return False, f"[Mosquitto - errore] Mosquitto è in modalità only local."

        # altrimenti semplicemente non è attivo
        return False, f"[Mosquitto - info] Mosquitto non è attivo"

    except Exception as e:
        return False, f"[Mosquitto - errore] Errore durante la verifica di Mosquitto: {e}"




## Chiude Mosquitto terminando tutti i processi "mosquitto"
def _chiudi_mosquitto():
    try:
        # pids = lista processi con nome "mosquitto"
        result = subprocess.run(['pgrep', '-f', 'mosquitto'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pids = result.stdout.strip().split()

        # se non ci sono processi, restituisci un messaggio errore
        if not pids:
            return False, "[Mosquitto - Errore] Nessun processo Mosquitto trovato."
        
        # se ci sono, termina tutti i processi con nome "mosquitto"
        for pid in pids:
            os.kill(int(pid), signal.SIGTERM)
            
        return True, "[Mosquitto - successo] Mosquitto terminato con successo."
    
    except Exception as e:
        return False, f"[Mosquitto - errore] Errore durante la chiusura di Mosquitto: {e}"



## Avvia un processo Mosquitto in background 
# !! in modalità globale (ascolta su tutte le interfacce)
def _avvia_mosquitto():
    try:
        # avvia un processo in background, con il comando 'mosquitto -c <file di configurazione>'
        subprocess.Popen(['mosquitto', '-c', mosquitto_config_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(2)   # attende 2 secondi per dare il tempo a Mosquitto di avviarsi
        
        # verifica se si è attivato
        isAttivo, verifica_msg = _mosquitto_is_attivo()
        if isAttivo:
            return True, "[Mosquitto - info] Mosquitto è stato avviato con successo. "
        else:
            return False, "[Mosquitto - errore] Mosquitto non si è avviato correttamente. "
        
    except Exception as e:
        return False, f"[Mosquitto - errore] Errore durante l'avvio di Mosquitto: {e}"


#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------

# FUNZIONE PER CANCELLARE I DATI DAL DATABASE  (DEBGGING, la inserisco qui temporaneamente)

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta

# === Configurazione ===
url = "http://localhost:8086"
token = "9-6z3SNN0R3X5H5nxjwda0DqShJXyCC9VQrfSVayP63NCTh7CA0SSetamkFNhlPXl3jv-uk7w3jONgK1fX9zXw=="
org = "RCAR"  
bucket = "CarSensors"

# === Connessione ===
client = InfluxDBClient(url=url, token=token, org=org)
delete_api = client.delete_api()

# === Intervallo di tempo da cancellare (tutti i dati) ===
start = "1970-01-01T00:00:00Z"  # inizio epoca UNIX
stop = datetime.utcnow().isoformat("T") + "Z"  # adesso (UTC in formato ISO)

# === Esegui cancellazione ===
def cancellaDati():    
    delete_api.delete(start, stop, "", bucket=bucket, org=org)
    print(f"Tutti i dati nel bucket '{bucket}' sono stati cancellati.")