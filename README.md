# Sviluppo di un veicolo terrestre a controllo remoto

## Tesi triennale in informatica - Marco Catanzaro

Questo progetto costituisce la mia tesi di laurea triennale in Informatica presso l'Università degli Studi di Udine, realizzata a seguito di un tirocinio svolto nel "Laboratorio di droni e sistemi autonomi". L'obiettivo principale è sviluppare un veicolo terrestre a controllo remoto, impiegando tecnologie avanzate per il controllo e la gestione dei dati.

### Struttura del progetto

Il progetto nasce dal recupero di una macchina radiocomandata degli anni '80, alla quale sono state rimosse le componenti originali per essere sostituite con tecnologie moderne. Il cuore del sistema è un **Raspberry Pi 3+**, affiancato da driver motori come **L298N** e una vasta gamma di sensori e attuatori: sensori a ultrasuoni per la rilevazione degli ostacoli, accelerometri per il monitoraggio del movimento, buzzer per segnalazioni acustiche, sensori di tensione per il controllo dell'alimentazione, oltre a videocamere e microfoni per la raccolta di dati visivi e sonori. Questa trasformazione consente di integrare funzionalità avanzate e di sperimentare soluzioni innovative nel campo dei veicoli autonomi.

### Obiettivi futuri

Attualmente, tutti i dati passati tramite **MQTT** e raccolti dai sensori vengono memorizzati in un **database InfluxDB** timestamp based e utilizzati in tempo reale per la generazione di grafici e strumenti visivi di supporto alle decisioni durante il pilotaggio remoto.

Un possibile sviluppo futuro del progetto consiste nell'integrare un **agente di intelligenza artificiale**, capace di analizzare i dati in tempo reale e prendere decisioni autonome sulla guida del veicolo. Questo permetterebbe di trasformare il sistema da semplice veicolo radiocomandato a piattaforma intelligente, in grado di adattarsi dinamicamente all'ambiente e migliorare l'efficienza operativa.





### Codice del progetto

Il codice si articola in due componenti principali:

1. **Software a bordo del Raspberry Pi**  
    Implementa un server multithread che gestisce simultaneamente i sensori, lo streaming audio/video e il controllo dei motori del veicolo.

2. **Software sul PC di controllo**  
    Include la logica per l'invio dei comandi, il broker MQTT (**Mosquitto**) e il database (**InfluxDB**). È presente anche un'**interfaccia grafica** che semplifica la gestione e l'avvio dei vari servizi.



### Obiettivi

- Sviluppare un sistema affidabile per il controllo remoto del veicolo.
- Implementare una comunicazione efficiente tra il veicolo e il sistema di controllo.
- Garantire la raccolta e la visualizzazione dei dati in tempo reale.

### Tecnologie utilizzate

- **Python**: Linguaggio principale per lo sviluppo del software.
- **MQTT**: Protocollo leggero e affidabile per la comunicazione tra il veicolo e il sistema di controllo remoto.
- **Pygame**: Libreria per la creazione di un'interfaccia grafica intuitiva e interattiva.
- **GStreamer**: Framework avanzato per lo streaming audio/video.
- **Socket UDP**: Protocollo per la trasmissione di dati in tempo reale.
- **InfluxDB**: Database per la memorizzazione dei dati dei sensori.
- **Mosquitto**: Broker MQTT per la gestione della comunicazione.
- **RPi.GPIO**: Libreria per il controllo dei pin GPIO del Raspberry Pi.
- **Adafruit CircuitPython**: Libreria per la gestione di sensori avanzati.
- **OpenCV**: Libreria per l'elaborazione di immagini e video.
- **Pillow**: Libreria per la manipolazione di immagini.
- **NumPy**: Libreria per il calcolo numerico e la gestione dei dati dei sensori.

Queste tecnologie lavorano insieme per creare un sistema innovativo e all'avanguardia, capace di attirare l'attenzione di chiunque sia interessato al mondo dei veicoli autonomi e del controllo remoto.

Grazie per l'interesse nel mio progetto! Se hai domande o suggerimenti, non esitare a contattarmi.