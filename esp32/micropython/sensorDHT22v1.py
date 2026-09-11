from machine import Pin
from utime import sleep
import dht

NOMBRE_ARCHIVO = "datos_met.csv"

sensor_dht22 = dht.DHT22(Pin(13))

def guardar_datos(t, h):
    try:
        with open(NOMBRE_ARCHIVO, "a") as f:
            f.write("{:.1f},{:.1f}\n".format(t, h))
    except OSError as e:
        print("Error al escribir archivo:", e)

# Crear el encabezado solo si el archivo no existe
try:
    with open(NOMBRE_ARCHIVO, "r"):
        pass
except OSError:
    with open(NOMBRE_ARCHIVO, "w") as f:
        f.write("temperatura,humedad\n")

while True:
    try:
        sensor_dht22.measure()
        t = sensor_dht22.temperature()
        h = sensor_dht22.humidity()
        
        print(f"Temp : {t} / hum : {h}")
        guardar_datos(t, h)
        sleep(2)
        print("")
        
    except OSError as e:
        print("Error data")

