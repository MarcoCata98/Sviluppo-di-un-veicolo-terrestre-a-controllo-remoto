import subprocess
import signal
import sys


class GStreamerStreamer:
    def __init__(self, ip_destinatario, porta_video, porta_audio):
        self.ip_destinatario = ip_destinatario
        self.porta_video = porta_video
        self.porta_audio = porta_audio

        self.proc = None

    def build_cmd(self):
        return [
            "gst-launch-1.0",
            "-v",
            "v4l2src", "device=/dev/video0",
            "!", "videoconvert",
            "!", "x264enc", "tune=zerolatency", "bitrate=500", "speed-preset=ultrafast",
            "!", "rtph264pay", "config-interval=1", "pt=96",
            "!", "udpsink", f"host={self.ip_destinatario}", f"port={self.porta_video}",

            "alsasrc", "device=hw:2,0",
            "!", "audioconvert", "!", "audioresample",
            "!", "opusenc",
            "!", "rtpopuspay", "pt=97",
            "!", "udpsink", f"host={self.ip_destinatario}", f"port={self.porta_audio}"
        ]

    # fa partire un nuovo processo con il comando gst-launch-1.0, con riferimento self.proc
    def start(self):
        cmd = self.build_cmd()
        try:
            print(f"Avvio streaming GStreamer verso {self.ip_destinatario}...")
            self.proc = subprocess.Popen(cmd, start_new_session=True)
            self.proc.wait()
        except KeyboardInterrupt:
            self.stop()


    # prende il processo self.proc e lo termina
    def stop(self):
        if self.proc:
            print("\n Interruzione richiesta: termino lo streaming...")
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            print("Streaming terminato correttamente.")
        sys.exit(0)


# COME GLI ALTRI SENSORI, SARA' NECESSARIO UN THREAD SEPARATO PER GESTIRE LO STREAMING

