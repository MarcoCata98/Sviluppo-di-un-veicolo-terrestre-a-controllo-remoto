# GUI.py
# Interfaccia grafica con i vari pulsanti per gestire i servizi e avviare gli script

import pygame
import threading
import subprocess
import time
import os
import sys
import socket
from ManageServizi import avvia_influxdb, chiudi_influxdb, verifica_influxdb, avvia_mosquitto, chiudi_mosquitto, verifica_mosquitto, cancellaDati


ip_locale = "0.0.0.0"           # Variabile globale per l'IP locale del pc di controllo
ip_raspberry = "0.0.0.0"        # Variabile globale per l'IP del Raspberry
nome_raspberry = "Marco.local"  # Nome host del Raspberry (per trovare l'IP)
stato_influxdb = None           # Variabile globale per lo stato di InfluxDB (True/False)
stato_mosquitto = None          # Variabile globale per lo stato di Mosquitto (True/False)

messaggi_log = []         # Lista per i messaggi di log  (visualizzati in basso nella console "fittizia") 


# === Funzioni base ===

# dato un messaggio lo aggiunge alla lista dei messaggi di log
def scrivi_log(testo):
    messaggi_log.append(testo)
    if len(messaggi_log) > 6:
        messaggi_log.pop(0)

# Ottiene l'IP locale e aggiorna la variabile globale ip_locale
def aggiorna_ip():
    global ip_locale
    try:
        # crea una socket UDP per connettersi a un server esterno, e da li ricava il proprio IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_locale = s.getsockname()[0]
        s.close()
        scrivi_log("!! IP aggiornato: " + ip_locale) 
    except Exception as e:
        ip_locale = f"Errore IP"
        scrivi_log(f"[Errore aggiornamento IP]: {e}")


# il raspberry ha un nome host (es. Marco.local), inserito in fase di configurazione
# socket.gethostbyname può essere usato per ottenere l'IP dal nome host
# una volta cliccato il pulsante, puoi recuperare facilmente l'ip da passare come argomento agli script
def trova_ip_raspberry():
    global ip_raspberry
    global nome_raspberry
    try:
        ip = socket.gethostbyname(nome_raspberry)
        scrivi_log(f"[IP trovato] IP del Raspberry ({nome_raspberry}): {ip}")
        ip_raspberry = ip
    except socket.gaierror:
        scrivi_log(f"[errore] dispositivo raspberry {nome_raspberry} non trovato !")
        return None



#------------------------------------------------------------------------

# Verifica se InfluxDB e Mosquitto sono attivi, e aggiorna le variabili globali stato_influxdb e stato_mosquitto
# la funzione viene richiamata ogni tot secondi per verificare che i servizi siano ancora attivi e funzionanti
def aggiorna_stati():
    global stato_influxdb, stato_mosquitto
    try:
        stato_influxdb, msg_influxdb = verifica_influxdb()
        stato_mosquitto, msg_mosquitto = verifica_mosquitto()
    except Exception as e:
        scrivi_log(f"[Errore stato influx o mosquitto]: {e}")



#------------------------------------------------------------------------

# esegue una funzione in un thread separato, per non bloccare l'interfaccia grafica
# però questo non mi permette di visualizzare direttamente l'output della funzione sul terminale
def Esegui_funzione_senza_terminale(funzione, descrizione="Operazione completata"):
    def wrapped():
        # vedo se la funzione non da errore
        try:
            funzione()
            if descrizione != "":
                scrivi_log(f" {descrizione}")   # una volta completata la funzione, scrivo descrizione nei log
        except Exception as e:
            scrivi_log(f" Errore: {e}")

    # la eseguo in un thread separato
    threading.Thread(target=wrapped, daemon=True).start()



# apre un terminale e lancia il file python specificato (con eventuale argomento)
# in modo che l'utente possa vedere il terminale con i messaggi di output dello script
def Esegui_file_con_terminale(percorso_file, argomento=None):

    '''
         - viene creato uno script temporaneo .command (macOS/Linux) o .bat (Windows)
         - nello script viene detto eseguire un codice python con eventuale argomento
         - e fai vedere l'output in un nuovo terminale      

    '''

    # genero i path 
    path_script = os.path.abspath(os.path.join("gui", percorso_file))  
    path_temp = os.path.join("/tmp", f"esegui_{os.path.basename(percorso_file)}.command") 

    if not os.path.exists(path_script):
        scrivi_log(f" File non trovato: {percorso_file}")
        return

    # scrittura del file temporaneo .command
    with open(path_temp, "w") as f:
        f.write("#!/bin/bash\n")      # script bash per macOS/Linux
        if argomento:
            f.write(f"/usr/bin/python3 \"{path_script}\" {argomento}\n")  # esegui file .py con argomento
        else:
            f.write(f"/usr/bin/python3 \"{path_script}\"\n")  # esegui file .py

        f.write("exec $SHELL\n")   # mantiene aperto il terminale dopo la chiusura dello script

    os.chmod(path_temp, 0o755)  # permessi di esecuzione

    try:
        subprocess.Popen(["open", "-a", "Terminal", path_temp])
        scrivi_log(f" avvio su terminale esterno {percorso_file} + " " + {argomento}" if argomento else "")

    except Exception as e:
        scrivi_log(f" Errore apertura console: {e}")




# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

# === Impostazioni Grafiche Pygame ===


pygame.init()
LARGHEZZA, ALTEZZA = 900, 560
schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Pannello di Controllo RC Car")
FONT = pygame.font.SysFont("consolas", 20)
SFONDO = (30, 30, 30)
BIANCO = (255, 255, 255)
VERDE = (0, 200, 0)
ROSSO = (200, 0, 0)
GRIGIO = (60, 60, 60)
AZZURRO = (90, 90, 255)


class CampoTesto:
    def __init__(self, x, y, w, h, testo_iniziale=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.colore = (255, 255, 255)
        self.testo = testo_iniziale
        self.attivo = False

    def gestisci_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.attivo = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.attivo:
            if event.key == pygame.K_RETURN:
                self.attivo = False
            elif event.key == pygame.K_BACKSPACE:
                self.testo = self.testo[:-1]
            else:
                self.testo += event.unicode

    def disegna(self, superficie):
        pygame.draw.rect(superficie, self.colore, self.rect, 2)
        txt_surface = FONT.render(self.testo, True, self.colore)
        superficie.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        if self.attivo:
            cursore_x = self.rect.x + 5 + txt_surface.get_width() + 2
            pygame.draw.line(superficie, self.colore, (cursore_x, self.rect.y + 5), (cursore_x, self.rect.y + 25), 2)

    def get_valore(self):
        return self.testo


# -------------------------------------------------------------------------
# ------------------------------------------------------------------------

# === Classe bottone ===


class Bottone:
    def __init__(self, x, y, w, h, testo, funzione, colore=AZZURRO):
        self.rect = pygame.Rect(x, y, w, h)
        self.testo = testo
        self.funzione = funzione   # funzione attivata al click
        self.colore = colore

    def disegna(self, superficie):
        pygame.draw.rect(superficie, self.colore, self.rect)
        txt = FONT.render(self.testo, True, BIANCO)
        superficie.blit(txt, (self.rect.x + 10, self.rect.y + 5))

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.funzione()

# -------------------------------------------------------------------------

# Campo di testo per inserire l'IP del raspberry

# è la sezione dove è possibile scrivere l'ip del raspberry, 
# se lo si conosce o lo si ricerca con il tasto "Trova IP Raspberry"
campo_ip = CampoTesto(480, 290, 200, 30, "192.168.1.101")
#  questo è un ip di default, cambiando la scritta cambia anche il valore

# -------------------------------------------------------------------------

# COSTRUZIONE GRIGLIA BOTTONI


# vengono inserite una serie di righe , ognuna con uno o più bottoni
bottoni = []

# passo un array di tuple (testo interno tasto, funzione da eseguire)
# ne costruisce un istanza di Bottone e li posiziona nella riga
# y = coordinata y della riga dal alto verso il basso
def aggiungi_riga(y, elementi):
    x = 10
    for testo, funzione in elementi:
        bottoni.append(Bottone(x, y, 220, 30, testo, funzione))
        x += 230



# riga [ [aggiorna ip pc locale] e [trova ip raspberry] ]
aggiungi_riga(10, [
    ("Aggiorna IP", lambda: Esegui_funzione_senza_terminale(aggiorna_ip, "")),
    ("Trova IP Raspberry", lambda: Esegui_funzione_senza_terminale(trova_ip_raspberry, ""))
])

# riga [ [avvia InfluxDB] e [chiudi InfluxDB] ]   e ne stampa il risultato nella console fittizia
aggiungi_riga(50, [
    ("Avvia InfluxDB", lambda: Esegui_funzione_senza_terminale(lambda: scrivi_log(avvia_influxdb()[1]), "")),
    ("Chiudi InfluxDB", lambda: Esegui_funzione_senza_terminale(lambda: scrivi_log(chiudi_influxdb()[1]), "")),
])

# riga [ [avvia Mosquitto] e [chiudi Mosquitto] ]
aggiungi_riga(90, [
    ("Avvia Mosquitto", lambda: Esegui_funzione_senza_terminale(lambda: scrivi_log(avvia_mosquitto()[1]), "")),
    ("Chiudi Mosquitto", lambda: Esegui_funzione_senza_terminale(lambda: scrivi_log(chiudi_mosquitto()[1]), "")),
])

# riga [ avvia ManagerDati ]  apre il terminale, in modo da vedere i messaggi di log
aggiungi_riga(130, [("Avvia ManagerDati", lambda: Esegui_file_con_terminale("ManagerDati.py"))])

# riga [ [avvia Lettura] e [visualizza Dati] ]   apre il terminale, in modo da vedere i messaggi di log
aggiungi_riga(170, [
    ("Avvia Lettura", lambda: Esegui_file_con_terminale("leggiDati.py")),
    ("Visualizza Dati", lambda: Esegui_file_con_terminale("visualizzaDati.py")),
])

# riga [ cancella Dati DB ]
aggiungi_riga(210, [("Cancella Dati DB", lambda: Esegui_funzione_senza_terminale(cancellaDati, "Dati cancellati"))])

# riga [ [Visualizza Stream] ] - apre un nuovo terminale, e si mette in attesa del arrivo dei pacchetti audio/video
aggiungi_riga(250, [("Visualizza Stream", lambda: Esegui_file_con_terminale("streaming_receiver.py"))])

# riga [ Muovi Macchina ]  - apro con un nuovo terminale e passo come argomento " ip raspberry " inserito nel campo ip
aggiungi_riga(290, [("Muovi Macchina", lambda: Esegui_file_con_terminale("ComandiMotore.py", campo_ip.get_valore()))])



#---------------------------------------------------------------------------------------------------------------

# === Main loop ===
# quando avvio il programma GUI

clock = pygame.time.Clock()
running = True

aggiorna_ip()
aggiorna_stati()

ultimo_check = 0

while running:
    schermo.fill(SFONDO)

    # Testi dinamici, si aggiornano a ogni ciclo del loop
    # ip_locale, stato_influxdb, stato_mosquitto (scritti in verde se attivi, rosso se non attivi)
    schermo.blit(FONT.render(f"IP questo PC: {ip_locale}", True, VERDE), (500, 15))
    schermo.blit(FONT.render(f"InfluxDB: {'Attivo' if stato_influxdb else 'Non Attivo'}", True, VERDE if stato_influxdb else ROSSO), (470, 60))
    schermo.blit(FONT.render(f"Mosquitto: {'Attivo' if stato_mosquitto else 'Non Attivo'}", True, VERDE if stato_mosquitto else ROSSO), (470, 100))


    # Controlla stato ogni 4 secondi di influxdb e mosquitto
    # quando cambia stato, il ciclo di servizio aggiorna la scritta in verde/rosso
    if time.time() - ultimo_check > 4:
        aggiorna_stati()
        ultimo_check = time.time()

    clock.tick(30)



    # Bottoni
    for bottone in bottoni:
        bottone.disegna(schermo)

    # Etichetta campo IP  (aggiornato il valore interno se modificata)
    schermo.blit(FONT.render("IP Raspberry:", True, BIANCO), (300, 295))
    campo_ip.disegna(schermo)

    # Console messaggi (con più spazio sopra)
    pygame.draw.rect(schermo, GRIGIO, (10, 340, 880, 200))
    for i, msg in enumerate(messaggi_log):
        schermo.blit(FONT.render(msg, True, BIANCO), (15, 345 + i * 25))

    pygame.display.flip()

    # Eventi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            campo_ip.gestisci_evento(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for bottone in bottoni:
                    bottone.click(pos)
                aggiorna_stati()

    

pygame.quit()
