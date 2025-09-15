# ComandiMotore.py
# Invia comandi WASD via UDP al Raspberry Pi per controllare il veicolo
# il serverPrincipale.py, estrarrà i comandi e li eseguirà

import pygame
import socket
import time
import sys



# aprendo il file tramite terminale, e passando come argomento l'IP del raspberry, verrà sostituito a questa costante
IP_RASPBERRY = sys.argv[1] if len(sys.argv) > 1 else "172.20.10.2" # nel caso default

# ho fissato la socket nel serverPrincipale.py a questa porta
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # e apro la socket mittente


#-------------------------------------------------------------------

 # === Pygame ===
 # APRO UNA FINESTRA PICCOLA, DA CUI POSSO INVIARE I COMANDI 
 # PYGAME SERVE PER RILEVARE I TASTI PREMUTI IN MODO FACILE

pygame.init()
screen = pygame.display.set_mode((300, 100))
pygame.display.set_caption("Controllo WASD")

clock = pygame.time.Clock()
ultimo_comando = ""


#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

# === Main Loop ===

# viene percepito il tasto premuto
running = True
while running:
    keys = pygame.key.get_pressed()

    w = keys[pygame.K_w]
    a = keys[pygame.K_a]
    s = keys[pygame.K_s]
    d = keys[pygame.K_d]
    k = keys[pygame.K_k]
    p = keys[pygame.K_p]

    comando = "fermo"


    # === COMANDI MOTORE ===

    if w and d:
        comando = "avanti+destra"
    elif w and a:
        comando = "avanti+sinistra"
    elif s and a:
        comando = "indietro+sinistra"
    elif s and d:
        comando = "indietro+destra"
    elif w:
        comando = "avanti"
    elif s:
        comando = "indietro"
    elif a:
        comando = "sinistra"
    elif d:
        comando = "destra"
    
    
    # === COMANDI CLACSON ===

    clacson_premuto = False

    if k and not clacson_premuto:
        sock.sendto(b"clacson_on", (IP_RASPBERRY, PORT))
        clacson_premuto = True
    elif not k and clacson_premuto:
        sock.sendto(b"clacson_off", (IP_RASPBERRY, PORT))
        clacson_premuto = False


    # === COMANDI STREAMING AUDIO/VIDEO ===

    streaming_cooldown = 2  # secondi di attesa da uno stream e l'altro, per evitare bug
    ultimo_streaming_time = 0   

    if p:
        tempo_attuale = time.time()
        if tempo_attuale - ultimo_streaming_time > streaming_cooldown: # un click ogni tot secondi
            sock.sendto(b"streaming", (IP_RASPBERRY, PORT))
            ultimo_streaming_time = tempo_attuale




#------------------------------------------------------------------------------------

    ## SEZIONE MIGLIORAMENTO DEL MOVIMENTO
    # rilasciando i comandi tramite "portasterzoa0" e "portatrazionea0" , si rende più fluido e reattivo il movimento

    if comando != ultimo_comando:
        comandi_correnti = set(comando.split("+"))
        comandi_prec = set(ultimo_comando.split("+"))

        # Se rilascio destra o sinistra, riporta lo sterzo a zero
        if "destra" in comandi_prec - comandi_correnti or "sinistra" in comandi_prec - comandi_correnti:
            sock.sendto(b"portasterzoa0", (IP_RASPBERRY, PORT))

        # Se rilascio avanti o indietro, ferma la trazione
        if "avanti" in comandi_prec - comandi_correnti or "indietro" in comandi_prec - comandi_correnti:
            sock.sendto(b"portatrazionea0", (IP_RASPBERRY, PORT))

        # Invia i nuovi comandi attivi
        for c in comandi_correnti:
            sock.sendto(c.encode(), (IP_RASPBERRY, PORT))
        ultimo_comando = comando


#------------------------------------------------------------------------------------

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False

    clock.tick(30)  # 30 FPS

# Invio comandi finali per fermare tutto
sock.sendto(b"fermo", (IP_RASPBERRY, PORT))
sock.sendto(b"stop", (IP_RASPBERRY, PORT))
pygame.quit()
