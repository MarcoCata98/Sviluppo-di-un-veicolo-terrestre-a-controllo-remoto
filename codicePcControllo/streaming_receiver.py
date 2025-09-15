#streaming_receiver.py
# Apre la socket di ricezione video/audio e avvia GStreamer per visualizzare il video in tempo reale

# Quando arrivano i pacchetti apre un riproduttore video/audio in automatico

import subprocess
import signal
import sys

PORTA_VIDEO = 5000
PORTA_AUDIO = 5001

# === Comando GStreamer per ricevere video e audio con bassa latenza ===
cmd = [
    "gst-launch-1.0", "-v",

    # === VIDEO ===
    "udpsrc", f"port={PORTA_VIDEO}", "caps=application/x-rtp,media=video,encoding-name=H264,payload=96",
    "!", "rtph264depay",
    "!", "avdec_h264",
    "!", "videoconvert",
    "!", "fpsdisplaysink", "sync=false", "text-overlay=false", "video-sink=autovideosink",

    # === AUDIO ===
    "udpsrc", f"port={PORTA_AUDIO}", "caps=application/x-rtp,media=audio,encoding-name=OPUS,payload=97",
    "!", "rtpopusdepay",
    "!", "opusdec",
    "!", "audioconvert",
    "!", "audioresample",
    "!", "autoaudiosink", "sync=false"
]


def main():
    try:
        print(f"[Gstreamer] Avvio ricezione video/audio in tempo reale...")
        # Avvia un nuovo processo ed esegui il comando per attivare GStreamer
        proc = subprocess.Popen(cmd, start_new_session=True)
        proc.wait() # si mette inattesa del arrivo dei pacchetti
    
    # chiudo e termino il processo in caso di interruzione con CTRL+C
    except KeyboardInterrupt:
        print("[Gstreamer] Interruzione richiesta: chiudo il receiver...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("[Gstreamer] Receiver chiuso correttamente.")
        sys.exit(0)

if __name__ == "__main__":
    main()

