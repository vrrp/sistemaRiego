from machine import Pin
from utime import sleep
import dht
import network
import urequests
import ujson
import ubinascii
import ntptime
import time

# ============ CONFIGURA ESTAS 5 COSAS ============
WIFI_SSID = "NOMBRE_DE_TU_WIFI"
WIFI_PASS = "CLAVE_DE_TU_WIFI"
GITHUB_TOKEN = "PON_AQUI_TU_TOKEN"
REPO = "tu_usuario/nombre_repositorio"
ZONA_HORARIA = -5   # UTC-5 = Peru/Colombia/Ecuador (cambialo si vives en otro lado)
# =================================================

NOMBRE_LOCAL = "datos_met.csv"      # archivo en la memoria del ESP32
NOMBRE_EN_GITHUB = "datos_met.csv"  # nombre que tendrá en GitHub
ENVIAR_CADA = 10                    # cada cuántas lecturas enviar a GitHub

sensor_dht22 = dht.DHT22(Pin(13))

def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print("Conectando al WiFi...")
        wifi.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(30):
            if wifi.isconnected():
                break
            sleep(1)
    if wifi.isconnected():
        print("WiFi conectado. IP:", wifi.ifconfig()[0])
    else:
        print("No se pudo conectar al WiFi")
    return wifi.isconnected()

def sincronizar_reloj():
    """Pregunta la hora al servidor NTP (el ESP32 no sabe la hora solo)."""
    try:
        print("Preguntando la hora por internet...")
        ntptime.settime()   # ajusta el reloj interno con la hora mundial (UTC)
        print("Reloj sincronizado.")
    except OSError:
        print("No se pudo sincronizar la hora (seguira con hora incorrecta)")

def fecha_hora():
    """Devuelve la fecha y hora local con formato 2026-09-11 12:49:33"""
    hora_local = time.time() + ZONA_HORARIA * 3600  # sumar/quitar las horas de tu pais
    anio, mes, dia, hora, minuto, segundo, _, _ = time.localtime(hora_local)
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        anio, mes, dia, hora, minuto, segundo)

def guardar_datos(t, h):
    try:
        with open(NOMBRE_LOCAL, "a") as f:
            f.write(fecha_hora() + ",{:.1f},{:.1f}\n".format(t, h))
    except OSError as e:
        print("Error al escribir archivo:", e)

def enviar_a_github():
    try:
        with open(NOMBRE_LOCAL, "r") as f:
            datos = f.read()
    except OSError:
        print("Todavia no existe el CSV en el ESP32")
        return

    contenido_b64 = ubinascii.b2a_base64(datos.encode()).decode().strip()

    url = "https://api.github.com/repos/{}/contents/{}".format(REPO, NOMBRE_EN_GITHUB)
    cabecera = {"Authorization": "token " + GITHUB_TOKEN}

    resp = urequests.get(url, headers=cabecera)
    if resp.status_code == 200:
        sha = resp.json()["sha"]
    else:
        sha = None
    resp.close()

    mensaje = "Datos del sensor DHT22"
    if sha is not None:
        cuerpo = ujson.dumps({"message": mensaje, "content": contenido_b64, "sha": sha})
    else:
        cuerpo = ujson.dumps({"message": mensaje, "content": contenido_b64})

    resp = urequests.put(url, data=cuerpo, headers=cabecera)
    if resp.status_code in (200, 201):
        print("Enviado a GitHub!")
    else:
        print("Error al enviar. Codigo:", resp.status_code)
    resp.close()

# Encabezado del CSV si no existe (ahora con columna de fecha)
try:
    with open(NOMBRE_LOCAL, "r"):
        pass
except OSError:
    with open(NOMBRE_LOCAL, "w") as f:
        f.write("fecha_hora,temperatura,humedad\n")

# Al encender: conectar, preguntar la hora, y enviar lo que haya guardado
if conectar_wifi():
    sincronizar_reloj()
    enviar_a_github()

contador = 0
while True:
    try:
        sensor_dht22.measure()
        t = round(sensor_dht22.temperature(), 1)
        h = round(sensor_dht22.humidity(),1 )
        
        print(fecha_hora(), "| Temp:", t, "| HR:", h)
        guardar_datos(t, h)
        
        contador += 1
        if contador >= ENVIAR_CADA:
            if conectar_wifi():
                enviar_a_github()
            contador = 0
        
        sleep(2)
        
    except OSError as e:
        print("Error data")
