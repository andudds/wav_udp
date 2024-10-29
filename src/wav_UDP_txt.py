import pygame
import socket
import time
import os
import subprocess
from colorama import init, Fore

# Inicializar colorama para habilitar colores en terminal
init(autoreset=True)

# Función para imprimir en colores
def print_colored(text, color):
    print(color + text)

# Función para leer el archivo de configuración
def read_config(filename):
    config = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignorar líneas vacías y comentarios
                    key, value = line.split("=")
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Archivo de configuración {filename} no encontrado.")
    except Exception as e:
        print(f"Error leyendo el archivo de configuración: {e}")
    return config


# Configuración de red: Obtener la IP estática
def set_static_ip(static_ip):
    try:
        with open("/etc/dhcpcd.conf", "a") as dhcpcd_conf:
            dhcpcd_conf.write(f"\ninterface eth0\nstatic ip_address={static_ip}/24\n")
            dhcpcd_conf.write("static routers=192.168.2.1\n")
            dhcpcd_conf.write("static domain_name_servers=8.8.8.8 8.8.4.4\n")
        subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], check=True)
        print(f"IP estática {static_ip} aplicada.")
    except Exception as e:
        print(f"Error al aplicar la IP estática: {e}")


# Intentar DHCP y aplicar IP estática si no se obtiene una IP
def set_ip(static_ip):
    try:
        print("Intentando obtener IP vía DHCP...")
        subprocess.run(["sudo", "dhclient", "eth0"], check=True)
        time.sleep(10)  # Esperar 10 segundos para que el DHCP asigne una IP

        ip_address = get_ip_address()
        if ip_address:
            print(f"IP asignada vía DHCP: {ip_address}")
        elif static_ip:
            print("No se obtuvo una IP vía DHCP. Aplicando IP estática...")
            set_static_ip(static_ip)
        else:
            print("No se encontró STATIC_IP en config.txt.")
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando DHCP: {e}")


# Función para obtener la IP actual de eth0
def get_ip_address():
    try:
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True, check=True)
        ip_address = result.stdout.strip().split()[0]  # Tomar la primera IP en caso de múltiples interfaces
        return ip_address if ip_address else None
    except Exception as e:
        print(f"Error obteniendo la IP: {e}")
        return None


# Inicializar el socket UDP
def initialize_socket(udp_ip, udp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)  # Timeout para intentar reconexiones
    return sock


# Función para verificar conexión UDP
def check_connection(sock, udp_ip, udp_port):
    test_message = b"test"
    attempts = 0
    while attempts < 5:  # Límite de intentos para evitar loops infinitos
        try:
            sock.sendto(test_message, (udp_ip, udp_port))
            print("Conexión establecida con el destino UDP.")
            return True
        except socket.error as e:
            print(f"No se pudo conectar: {e}. Reintentando en 5 segundos...")
            time.sleep(5)  # Espera 5 segundos antes de reintentar
            attempts += 1
    return False


# Función para inicializar pygame y cargar el audio
def initialize_audio(audio_file):
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    if os.path.exists(audio_file):
        pygame.mixer.music.load(audio_file)
        return True
    else:
        print(f"Archivo de audio {audio_file} no encontrado.")
        return False


# Función para reproducir el audio en loop
def play_audio():
    pygame.mixer.music.play()


# Función principal para gestionar la reproducción y los eventos
def main_loop(sock, udp_ip, udp_port, event_times, audio_duration):
    last_event_index = 0
    play_audio()  # Iniciar la reproducción del audio

    while True:
        # Obtener el tiempo actual de reproducción
        current_time = pygame.mixer.music.get_pos() / 1000  # en segundos
        if current_time == -1:  # Revisar si la reproducción está detenida
            time.sleep(0.1)
            continue

        # Enviar evento UDP en tiempos especificados
        if last_event_index < len(event_times) and int(current_time) == event_times[last_event_index]:
            message = f"Evento en {event_times[last_event_index]} segundos".encode()
            try:
                sock.sendto(message, (udp_ip, udp_port))
                print(f"Mensaje enviado: {message}")
            except socket.error as e:
                print(f"Error al enviar mensaje UDP: {e}")
            last_event_index += 1

        # Reiniciar el audio y los eventos al final del loop
        if current_time >= audio_duration or not pygame.mixer.music.get_busy():
            last_event_index = 0
            play_audio()  # Reiniciar el audio

        time.sleep(0.1)  # Pausa para no sobrecargar el CPU


# Cargar configuración desde archivo
config = read_config("/boot/configScript.txt")

# Configuración de red
static_ip = config.get("STATIC_IP", None)
print_colored(f"STATIC_IP desde archivo de configuración: {static_ip}", Fore.GREEN)
set_ip(static_ip)

# Obtener valores de configuración
udp_ip = config.get("UDP_IP", "127.0.0.1")
print_colored(f"IP de destino UDP: {udp_ip}", Fore.YELLOW)
udp_port = int(config.get("UDP_PORT", 12000))
print_colored(f"Puerto de destino UDP: {udp_port}", Fore.BLUE)
audio_file = config.get("AUDIO_FILE", "default.wav")
print_colored(f"Archivo de audio: {audio_file}", Fore.CYAN)
event_times = list(map(int, config.get("EVENT_TIMES", "10,20,30,60").split(",")))
print_colored(f"Tiempos de eventos: {event_times}", Fore.MAGENTA)
audio_duration = int(config.get("AUDIO_DURATION", 70))
print_colored(f"Duración del audio: {audio_duration} segundos", Fore.WHITE)

# Inicializar socket UDP y verificar conexión
sock = initialize_socket(udp_ip, udp_port)
if check_connection(sock, udp_ip, udp_port):
    # Inicializar audio y comenzar la reproducción si todo está listo
    if initialize_audio(audio_file):
        main_loop(sock, udp_ip, udp_port, event_times, audio_duration)
    else:
        print("No se puede iniciar la reproducción de audio.")
else:
    print("No se pudo establecer conexión UDP.")
