'''
ServerPrincipale.py

E' il thread principale che gestisce i movimenti del veicolo
e istanzia i thread separati per ogni singolo sensore, attuatore e videocamera

'''


import socket
import time
import threading
import motori
from voltageSensor import VoltageReader
from buzzer import Buzzer
from ultrasoundSensor import SensoreUltrasuoni
from accelerometro import AccelerometroReader
from mqtt_sender import invia_messaggio_mqtt
from streaming_sender import GStreamerStreamer

# IP del broker MQTT (pc di controllo)
MQTT_BROKER = "192.168.1.100" 
MQTT_PORT = 1883

# IP del destinatario dello streaming (pc di controllo)
IP_DESTINATARIO = "192.168.1.100"  
PORTA_VIDEO = 5000
PORTA_AUDIO = 5001


'''

SEZIONE THREAD SEPARATI SENSORI E ATTUATORI

'''


# --- THREAD SENSORE VOLTAGGIO BATTERIA ---
# legge il voltaggio dal sensore, stampa in console e lo invia via tramite mqtt

voltage_reader = VoltageReader()

def monitor_batteria():
    while True:
        v = voltage_reader.leggi_batteria()
        invia_messaggio_mqtt("sensori/voltaggio", str(v), MQTT_BROKER, MQTT_PORT)
        print(f"[Monitor] Batteria: {v:.2f} V")
        time.sleep(1)

# Avvio thread
threadBatteria = threading.Thread(target=monitor_batteria, daemon=True)
threadBatteria.start()



# --- THREAD GESTORE BUZZER ---
# aziona il buzzer nel caso i sensori a ultrasuoni rilevino un ostacolo vicino
# oppure se il clacson viene attivato manualmente tramite comando UDP

BUZZER_PIN = 4  # GPIO 4 = pin fisico 7
buzzer = Buzzer(BUZZER_PIN)

clacson_attivo = False
allarme_centrale = False
allarme_dx = False
allarme_sx = False

def gestisci_clacson():
    while True:
        if clacson_attivo or allarme_centrale or allarme_dx or allarme_sx:
            buzzer.accendi_buzzer()
        else:
            buzzer.spegni_buzzer()
        time.sleep(0.05)


threadClacson = threading.Thread(target=gestisci_clacson, daemon=True)
threadClacson.start()




# -- THREAD SENSORI A ULTRASUONI --
# per ognuno dei tre sensori a ultrasuoni viene creato un thread separato
# che legge la distanza, la stampa in console e la invia via mqtt
# se la distanza è inferiore a Distanza_minima attiva il clacson

Distanza_minima = 20  # il sensore ritorna il valore in cm


# Sensore centrale (davanti)

sensore_centrale = SensoreUltrasuoni(trigger_pin=14, echo_pin=15)

def monitor_ultrasuoni():
    while True:
        distanza = sensore_centrale.misura_distanza_cm()
        print(f"[Ultrasuoni] Oggetto a {distanza} cm")
        time.sleep(0.3)  


def monitor_ultrasuoni_buzz_davanti():
    global allarme_centrale  

    while True:
        distanza = sensore_centrale.misura_distanza_cm()
        if distanza is not None:
            invia_messaggio_mqtt("sensori/ultrasuoni/davanti", str(distanza), MQTT_BROKER, MQTT_PORT)
            print(f"[Ultrasuoni DAV] Oggetto a {distanza} cm")

            # Clacson automatico se troppo vicino
            if distanza < Distanza_minima:
                allarme_centrale = True
            else:
                allarme_centrale = False
        else:
            print("[Ultrasuoni] Lettura scartata")
            allarme_centrale = False

        time.sleep(0.2)

threading.Thread(target=monitor_ultrasuoni_buzz_davanti, daemon=True).start()



# Sensore destro (dx)

sensore_dx = SensoreUltrasuoni(trigger_pin=17, echo_pin=27)


def monitor_ultrasuoni_buzz_destro():
    global allarme_dx 

    while True:
        distanza = sensore_dx.misura_distanza_cm()
        if distanza is not None:
            invia_messaggio_mqtt("sensori/ultrasuoni/dx", str(distanza), MQTT_BROKER, MQTT_PORT)
            print(f"[Ultrasuoni DX] Oggetto a {distanza} cm")

            # Clacson automatico se troppo vicino
            if distanza < Distanza_minima:
                allarme_dx = True
            else:
                allarme_dx = False
        else:
            print("[Ultrasuoni] Lettura scartata")
            allarme_dx = False 

        time.sleep(0.2)

threading.Thread(target=monitor_ultrasuoni_buzz_destro, daemon=True).start()



# sensore sinistro (sx)

sensore_sx = SensoreUltrasuoni(trigger_pin=22, echo_pin=25)

def monitor_ultrasuoni_buzz_sinistro():
    global allarme_sx  

    while True:
        distanza = sensore_sx.misura_distanza_cm()
        if distanza is not None:
            invia_messaggio_mqtt("sensori/ultrasuoni/sx", str(distanza), MQTT_BROKER, MQTT_PORT)
            print(f"[Ultrasuoni SX] Oggetto a {distanza} cm")

            # Clacson automatico se troppo vicino
            if distanza < Distanza_minima:
                allarme_sx = True
            else:
                allarme_sx = False
        else:
            print("[Ultrasuoni] Lettura scartata")
            allarme_sx = False

        time.sleep(0.2)

threading.Thread(target=monitor_ultrasuoni_buzz_sinistro, daemon=True).start()





# -- THREAD SENSORE ACCELEROMETRO ---
# legge l'accelerazione sui tre assi, la stampa in console e la invia via mqtt

accelerometro = AccelerometroReader()
accelerometro.calibra()


def monitor_accelerometro():
    while True:
        x, y, z = accelerometro.leggi()
        if x is not None:
            invia_messaggio_mqtt("sensori/accelerometro/x", str(x), MQTT_BROKER, MQTT_PORT)
            invia_messaggio_mqtt("sensori/accelerometro/y", str(y), MQTT_BROKER, MQTT_PORT)
            invia_messaggio_mqtt("sensori/accelerometro/z", str(z), MQTT_BROKER, MQTT_PORT)
            print(f"[Accelerometro] X={x} m/s²  Y={y} m/s²  Z={z} m/s²")
        time.sleep(0.5)

threading.Thread(target=monitor_accelerometro, daemon=True).start()


#------------------------------


# -- THREAD STREAMING VIDEO E AUDIO ---
# avvia lo streaming video/audio verso il pc di controllo quando riceve il comando "streaming"


streaming_attivo = False
streaming_instance = None

## in un nuovo thread, viene avviato il processo GstreamerStreamer.start(), cioè lo streaming
def avvia_streaming():
    global streaming_attivo
    global streaming_instance

    if not streaming_attivo:
        streaming_attivo = True
        print("[Streaming] Avvio streaming video/audio...")
        streaming_instance = GStreamerStreamer(IP_DESTINATARIO, PORTA_VIDEO, PORTA_AUDIO)
        threading.Thread(target=streaming_instance.start, daemon=True).start()
    else:
        print("[Streaming] Streaming già attivo.")


## termina il processo avviato dentro streaming_instance
def ferma_streaming():
    global streaming_attivo
    global streaming_instance

    if streaming_attivo:
        streaming_attivo = False
        print("[Streaming] Arresto streaming video/audio...")
        if streaming_instance is not None:
            streaming_instance.stop()
    else:
        print("[Streaming] Streaming già fermo.")


# scrivendo il codice in questo modo, posso accendere e spegnere lo streaming audio video



#----------------------------------------------------------------------
#----------------------------------------------------------------------

''' 

    Thread principale - gestisce i motori tramite i segnali che arrivano dalla socket UDP

'''

# Armare i motori - pwm attivi a potenza 0
motori.avviaMotore()


# SETUP SOCKET UDP
# ascolta su tutte le interfacce di rete alla porta 5005

IP = "0.0.0.0"
PORT = 5005

# istanzia la socket udp per ipv4
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    sock.bind((IP, PORT))
except OSError as e:
    print("porta già in uso, riavvio")
    exit(1)

print(f"[Server UDP] In ascolto su porta {PORT}")

#------------------------------------------------


# LOOP DI SISTEMA

try:
    while True:

        ## recvfrom: LEGGE IL PRIMO PACCHETTO IN CODA
        # ne estrae al massimo 1024 il resto butta via
        # noi inviamo parole tipo "avanti" = 64 byte
        data, addr = sock.recvfrom(1024)
        # poi trasformo da bit a stringa e la sistemo (tolgo spazi e minuscolo)
        comando = data.decode().strip().lower()

        ## !! recvfrom è bloccante !! 
        ## se non arrivano pacchetti rimane in attesa !

        print(comando)

        ## ESEGUE I COMANDI CHE GLI ARRIVANO
        if comando == "avanti":
            motori.avanti()
        elif comando == "indietro":
            motori.indietro()
        elif comando == "sinistra":
            motori.sinistra()
        elif comando == "destra":
            motori.destra()
        elif comando == "fermo":
            motori.fermo()
        elif comando == "portasterzoa0":
            motori.sterzo_a_zero()
        elif comando == "portatrazionea0":
            motori.trazione_a_zero()
        elif comando == "stop":
            break
        elif comando == "clacson_on":
           clacson_attivo = True
        elif comando == "clacson_off":
           clacson_attivo = False

        elif comando == "streaming":
            if not streaming_attivo:
                avvia_streaming()
            else:
                ferma_streaming()


# viene chiuso il server con il comando "stop" oppure con ctrl+c
except KeyboardInterrupt:
    print("Interrotto manualmente.")
finally:
    # pulisce la memoria del raspberry
    buzzer.cleanup_buzzer()
    motori.spegniMotore()
    print("Motori spenti e GPIO puliti.")



