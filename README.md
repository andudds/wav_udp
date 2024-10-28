# UDP Audio Project

Este proyecto reproduce audio en loop y envía mensajes UDP en intervalos específicos, diseñado para ejecutarse automáticamente en una Raspberry Pi al iniciar.

## Características

- Reproduce audio en loop en la Raspberry Pi.
- Envía mensajes UDP en momentos específicos definidos en `config.txt`.
- Se configura como un servicio `systemd` para iniciarse automáticamente al arrancar y reiniciar si falla.

## Configuración

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/udp_audio_project.git


2. En el archivo `configScript.txt` ubicado en directorio /boot de la sd de la raspberry puedes modificar los valores básicos de configuración como:

- UDP_IP: IP de destino.
- UDP_PORT: Puerto UDP de destino.
- AUDIO_FILE: Ruta al archivo .wav.
- EVENT_TIMES: Tiempos de los eventos en segundos, separados por comas.
- AUDIO_DURATION: Duración del audio en segundos (esto permite ajustar la duración cuando cambia el archivo de audio).





 - Para configurar tu script de Python para que se ejecute automáticamente al iniciar la Raspberry Pi, puedes usar systemd, que es un sistema de gestión de servicios en Linux. Con systemd, puedes crear un servicio que inicie el script al arrancar y controle si está en ejecución, reiniciándolo automáticamente si falla.


- Paso 1: Crear un Servicio de systemd Conéctate a la Raspberry Pi y crea un archivo de servicio en el directorio:

/etc/systemd/system/ 

- Vamos a llamarlo udp_audio.service:


sudo nano /etc/systemd/system/udp_audio.service


- En el archivo, agrega la siguiente configuración. Esto configura el servicio para que ejecute el script de Python en el arranque y supervise su estado.

[Unit]
Description=Servicio de audio UDP con Python
After=network.target

[Service]
ExecStart=/usr/bin/python3 /ruta/a/tu/script.py
Restart=always
RestartSec=5
User=pi  # Cambia esto a tu usuario si es diferente
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target


- Qué es cada cosa

- ExecStart: La ruta completa al intérprete de Python y a tu script. Asegúrate de que sea correcto.
- Restart=always: Hace que el servicio se reinicie automáticamente si se detiene inesperadamente.
- RestartSec=5: Configura un tiempo de espera de 5 segundos antes de intentar reiniciar el servicio.
- User=pi: Define el usuario que ejecutará el servicio (cámbialo según tu usuario en la Raspberry Pi).
- Environment=PYTHONUNBUFFERED=1: Esto garantiza que cualquier salida de consola o errores se impriman en tiempo real, útil para depuración.
Guarda el archivo y ciérralo (Ctrl+O para guardar y Ctrl+X para salir).

Paso 2: Habilitar y Arrancar el Servicio
Recarga systemd para que detecte el nuevo servicio:


sudo systemctl daemon-reload

Habilita el servicio para que se inicie automáticamente al arrancar la Raspberry Pi:

sudo systemctl enable udp_audio.service

Inicia el servicio por primera vez:

sudo systemctl start udp_audio.service

Paso 3: Verificar el Estado del Servicio
Para comprobar si el servicio está en ejecución y funcionando correctamente, puedes usar:

sudo systemctl status udp_audio.service

Esto mostrará el estado del servicio, si está en ejecución, y cualquier mensaje de error si ha fallado.

Paso 4: Ver los Logs para Depuración
Si necesitas ver la salida o los logs de tu script, puedes usar el comando journalctl:


sudo journalctl -u udp_audio.service -f

Este comando muestra los logs en tiempo real. Si deseas ver logs antiguos, simplemente omite el -f.

Paso 5: Reiniciar el Servicio Manualmente (Opcional)
Si necesitas reiniciar el servicio manualmente, puedes hacerlo con:


sudo systemctl restart udp_audio.service

Paso 6: Opcional - Supervisión de Estado y Reinicio
El servicio ya está configurado para reiniciarse automáticamente si falla. Sin embargo, si quieres asegurarte de que el script sigue ejecutándose correctamente, podrías agregar una verificación interna de estado en el script. Podrías usar un archivo de log para registrar eventos críticos, y luego analizar el log para ver si el script continúa funcionando.

Paso 7: Reiniciar la Raspberry para Comprobar el Arranque
Para asegurarte de que el script se ejecuta al arrancar, puedes reiniciar la Raspberry Pi y comprobar el estado del servicio después de que arranque:


sudo reboot

Luego, cuando la Raspberry esté en línea, 
verifica que el servicio está activo:


sudo systemctl status udp_audio.service

Este enfoque asegurará que el script de Python se ejecute en el arranque de la Raspberry Pi y se reinicie automáticamente en caso de fallo.
