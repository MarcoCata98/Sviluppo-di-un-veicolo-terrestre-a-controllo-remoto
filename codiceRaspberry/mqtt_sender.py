# mqtt_sender.py
# contiene la funzione per inviare messaggi MQTT al pc di controllo

import paho.mqtt.client as mqtt


# vengono passiti il topic e il valore da inviare
# quindi pubblicherà il valore sul topic specifico
def invia_messaggio_mqtt(topic: str, valore: str, broker_ip: str, broker_port: int):
    try:
        client = mqtt.Client()
        client.connect(broker_ip, broker_port, 60)              # si connette al broker MQTT
        client.publish(topic, valore)                           # pubblica il messaggio sul topic specifico
        client.disconnect()                                     # si disconnette dal broker MQTT     
        print(f"[MQTT] Inviato: '{valore}' su topic: {topic}")
    except Exception as e:
        print(f"[MQTT] Errore invio su topic {topic}: {e}")


#-----------------------------------------------------------------------------------

'''
    Non va molto bene a livello di prestazioni
    perchè ogni volta che deve inviare un messaggio si connette e disconnette dal broker 
    Produce molto overhead questa soluzione, rallentando di molto la trasmissione

    Una soluzione migliore sarebbe mantenere una connessione persistente con il broker per ogni sensore

            Per esempio un unico thread separato che mantiene la connessione aperta
            e ha il solo scopo di ricevere i messaggi dagli altri thread e inviarli al broker

            # Esempio di flusso con coda e thread dedicato:

            #    +-------------------+      +-------------------+
            #    | Thread Sensore 1  |      | Thread Sensore 2  |
            #    +-------------------+      +-------------------+
            #             |                      |
            #             v                      v
            #          +-------------------------------+
            #          |         Coda Messaggi         |
            #          +-------------------------------+
            #                      |
            #                      v
            #             +-------------------+
            #             | Thread MQTT Sender|
            #             +-------------------+
            #                      |  connessione persistente
            #                      v
            #               +--------------+
            #               |  MQTT Broker |
            #               +--------------+

'''
