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
ZONA_HORARIA = -5   # UTC-5 = Peru/Colombia/Ecuador (cambialo si vives en otro lado)
# =================================================

NOMBRE_LOCAL = "datos_met.csv"      # archivo en la memoria del ESP32
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

while True:
    try:
        sensor_dht22.measure()
        t = sensor_dht22.temperature()
        h = sensor_dht22.humidity()
        
        print(fecha_hora(), "| Temp:", t, "| HR:", h)
        guardar_datos(t, h)
        
        sleep(2)
        
    except OSError as e:
        print("Error data")

