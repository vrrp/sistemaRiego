import socket
import network
from utime import sleep

"""
wget http://192.168.1.45/datos_met.csv -O datos_met.csv
crontab -e
5 * * * * wget -q http://192.168.1.45/datos_met.csv -O /home/pi/datos_$(date +\%Y\%m\%d_\%H%M).csv


"""

WIFI_SSID = "NOMBRE_DE_TU_WIFI"
WIFI_PASS = "CLAVE_DE_TU_WIFI"

def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        wifi.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(30):
            if wifi.isconnected():
                break
            sleep(1)
    print("IP del ESP32:", wifi.ifconfig()[0])   # ¡Anota esta IP!

conectar_wifi()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 80))    # taquilla en el puerto 80
s.listen(1)
print("Servidor listo, esperando pedidos...")

while True:
    conn, direccion = s.accept()
    print("Pedido de:", direccion)
    try:
        conn.recv(512)   # leer el pedido HTTP (no nos importa qué pidieron)
        with open("datos_met.csv") as f:
            datos = f.read()
        conn.send("HTTP/1.0 200 OK\r\nContent-Type: text/csv\r\n\r\n")
        conn.sendall(datos.encode())
    except OSError:
        pass
    conn.close()

