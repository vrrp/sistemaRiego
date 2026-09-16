import socket
import network
from utime import sleep

WIFI_SSID = "NOMBRE_DE_TU_WIFI"
WIFI_PASS = "CLAVE_DE_TU_WIFI"

ENCABEZADO = "fecha_hora,temperatura,humedad\n"

def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        wifi.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(30):
            if wifi.isconnected():
                break
            sleep(1)
    print("IP del ESP32:", wifi.ifconfig()[0])

def leer_y_vaciar():
    """Lee el CSV y lo deja solo con el encabezado (buzon vacio)."""
    try:
        with open("datos_met.csv", "r") as f:
            datos = f.read()
    except OSError:
        datos = ENCABEZADO
    # Vaciar el buzon: dejar solo el encabezado para los datos nuevos
    with open("datos_met.csv", "w") as f:
        f.write(ENCABEZADO)
    return datos

conectar_wifi()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 80))
s.listen(1)
print("Servidor listo, esperando pedidos...")

while True:
    conn, direccion = s.accept()
    print("Pedido de:", direccion)
    try:
        conn.recv(512)
        datos = leer_y_vaciar()          # entregar Y vaciar en el mismo acto
        conn.send("HTTP/1.0 200 OK\r\nContent-Type: text/csv\r\n\r\n")
        conn.sendall(datos.encode())
        print("Enviados {} bytes. Buzon vaciado.".format(len(datos)))
    except OSError:
        print("Fallo al enviar (el buzon NO se vacio)")
    conn.close()

