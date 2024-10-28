import pygame
import socket
import time

# Función para leer el archivo de configuración
def read_config(filename):
    config = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignorar líneas vacías y comentarios
                key, value = line.split("=")
                config[key.strip()] = value.strip()
    return config

# Cargar configuración
config = read_config("config.txt")

# Configuración UDP y archivo de audio
UDP_IP = config.get("UDP_IP", "127.0.0.1")
UDP_PORT = int(config.get("UDP_PORT", 12000))
audio_file = config.get("AUDIO_FILE", "default.wav")
event_times = list(map(int, config.get("EVENT_TIMES", "10,20,30,60").split(",")))
audio_duration = int(config.get("AUDIO_DURATION", 70))

# Inicializar el socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Inicialización de pygame y carga del audio
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

# Función para reproducir el audio en loop
def play_audio():
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()  # Reproducir una vez y reiniciar manualmente al final

# Iniciar el audio en loop
play_audio()

# Índice de los eventos a enviar
last_event_index = 0

while True:
    # Obtener el tiempo actual de reproducción
    current_time = pygame.mixer.music.get_pos() / 1000  # en segundos

    # Verificar si `get_pos()` devuelve un valor válido
    if current_time == -1:
        time.sleep(0.1)
        continue  # Saltar el loop si `get_pos()` devolvió -1

    # Comprobar si estamos en el tiempo exacto de un evento
    if last_event_index < len(event_times) and int(current_time) == event_times[last_event_index]:
        # Enviar mensaje UDP
        message = f"Evento en {event_times[last_event_index]} segundos".encode()
        sock.sendto(message, (UDP_IP, UDP_PORT))
        
        print(f"Mensaje enviado: {message}")
        last_event_index += 1

    # Reiniciar el índice de eventos y audio al final del loop
    if current_time >= audio_duration or not pygame.mixer.music.get_busy():
        last_event_index = 0
        play_audio()  # Reiniciar el audio para la siguiente vuelta

    # Pausa para no sobrecargar el CPU
    time.sleep(0.1)
