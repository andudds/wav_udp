
# UDP Audio Project

Este proyecto reproduce audio en loop y envía mensajes UDP en intervalos específicos, diseñado para ejecutarse automáticamente en una Raspberry Pi al iniciar.

## Características

- **Reproduce audio en loop** en la Raspberry Pi.
- **Envía mensajes UDP** en momentos específicos definidos en `config.txt`.
- **Configurado como un servicio systemd** para iniciarse automáticamente al arrancar y reiniciarse si falla.

## Configuración

### Paso 1: Clonar el Repositorio

Clona el repositorio en tu Raspberry Pi:

```bash
git clone https://github.com/tu_usuario/udp_audio_project.git
```

### Paso 2: Configurar el Archivo `config.txt`

En el archivo `config.txt`, en la carpeta raiz del proyecto, puedes modificar los valores básicos de configuración:

- **UDP_IP**: IP de destino.
- **UDP_PORT**: Puerto UDP de destino.
- **AUDIO_FILE**: Ruta al archivo `.wav`.
- **EVENT_TIMES**: Tiempos de los eventos en segundos, separados por comas.
- **AUDIO_DURATION**: Duración del audio en segundos (esto permite ajustar la duración cuando cambia el archivo de audio).

Ejemplo de `config.txt`:

```plaintext
UDP_IP=192.168.0.123
UDP_PORT=12000
AUDIO_FILE=/ruta/a/tu/archivo.wav
EVENT_TIMES=10,20,30,60
AUDIO_DURATION=70
```

## Configuración del Servicio `systemd`

Para ejecutar el script automáticamente al iniciar la Raspberry Pi, configuraremos un servicio `systemd`. Este servicio monitorea el script y reinicia la ejecución en caso de que falle.

### Paso 1: Crear el Archivo de Servicio `systemd`

1. Conéctate a la Raspberry Pi y crea un archivo de servicio en el directorio `/etc/systemd/system/`:

    ```bash
    sudo nano /etc/systemd/system/udp_audio.service
    ```

2. En el archivo, agrega la siguiente configuración:

    ```ini
    [Unit]
    Description=Servicio de audio UDP con Python
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 /ruta/a/tu/script.py
    Restart=always
    RestartSec=5
    User=pi  # Cambia esto si tu usuario es diferente
    Environment=PYTHONUNBUFFERED=1

    [Install]
    WantedBy=multi-user.target
    ```

   **Explicación de cada parámetro**:

   - **`ExecStart`**: Ruta completa al intérprete de Python y al script. Asegúrate de que sea correcta.
   - **`Restart=always`**: Reinicia automáticamente el servicio si se detiene inesperadamente.
   - **`RestartSec=5`**: Espera 5 segundos antes de intentar reiniciar.
   - **`User=pi`**: Define el usuario que ejecutará el servicio (cámbialo si usas otro usuario).
   - **`Environment=PYTHONUNBUFFERED=1`**: Asegura que cualquier salida o error en la consola se imprima en tiempo real (útil para depuración).

3. Guarda el archivo y ciérralo (`Ctrl+O` para guardar y `Ctrl+X` para salir).

### Paso 2: Habilitar y Arrancar el Servicio

1. **Recarga `systemd`** para que detecte el nuevo servicio:

    ```bash
    sudo systemctl daemon-reload
    ```

2. **Habilita el servicio** para que se inicie automáticamente al arrancar la Raspberry Pi:

    ```bash
    sudo systemctl enable udp_audio.service
    ```

3. **Inicia el servicio** por primera vez:

    ```bash
    sudo systemctl start udp_audio.service
    ```

### Paso 3: Verificar el Estado del Servicio

Para comprobar si el servicio está en ejecución y funcionando correctamente, usa el comando:

```bash
sudo systemctl status udp_audio.service
```

Este comando muestra el estado del servicio, si está en ejecución y cualquier mensaje de error si ha fallado.

### Paso 4: Ver los Logs para Depuración

Si necesitas ver la salida o los logs de tu script, puedes usar `journalctl`:

```bash
sudo journalctl -u udp_audio.service -f
```

Este comando muestra los logs en tiempo real. Si deseas ver logs antiguos, simplemente omite el `-f`.

### Paso 5: Reiniciar el Servicio Manualmente (Opcional)

Si necesitas reiniciar el servicio manualmente, ejecuta:

```bash
sudo systemctl restart udp_audio.service
```

### Paso 6: Opcional - Supervisión de Estado y Reinicio

El servicio ya está configurado para reiniciarse automáticamente si falla. Sin embargo, si deseas asegurarte de que el script sigue ejecutándose correctamente, puedes agregar una verificación interna de estado en el script, como un archivo de log que registre eventos críticos.

### Paso 7: Reiniciar la Raspberry Pi para Comprobar el Arranque

Para asegurarte de que el script se ejecute al arrancar, puedes reiniciar la Raspberry Pi y comprobar el estado del servicio después de que arranque:

```bash
sudo reboot
```

Luego, cuando la Raspberry esté en línea, verifica que el servicio está activo:

```bash
sudo systemctl status udp_audio.service
```

Este enfoque asegurará que el script de Python se ejecute en el arranque de la Raspberry Pi y se reinicie automáticamente en caso de fallo.

---

## Licencia

Este proyecto está bajo la licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.
