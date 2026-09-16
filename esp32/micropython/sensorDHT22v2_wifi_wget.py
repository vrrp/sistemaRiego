from machine import Pin
from utime import sleep, sleep_ms, ticks_ms, ticks_diff
import dht
import network
import socket
import urequests
import ujson
import ubinascii
import ntptime
import time

# ============ CONFIGURA ESTAS COSAS ============
WIFI_SSID = "NOMBRE_DE_TU_WIFI"
WIFI_PASS = "CLAVE_DE_TU_WIFI"
GITHUB_TOKEN = "PON_AQUI_TU_TOKEN"
REPO = "tu_usuario/nombre_repositorio"
ZONA_HORARIA = -5
INTERVALO_ENVIO = 3600    # segundos = enviar a GitHub cada 1 hora
# ===============================================

NOMBRE_LOCAL = "datos_met.csv"
ENCABEZADO = "fecha_hora,temperatura,humedad\n"
INTERVALO_LECTURA = 2000  # milisegundos entre lecturas del sensor (2 s)

sensor_dht22 = dht.DHT22(Pin(13))
wifi = network.WLAN(network.STA_IF)

# ---------- WiFi ----------
def conectar_wifi():
    wifi.active(True)
    if wifi.isconnected():
        return True
    print("Conectando al WiFi...")
    try:
        wifi.connect(WIFI_SSID, WIFI_PASS)
    except OSError:
        pass
    for _ in range(30):
        if wifi.isconnected():
            print("WiFi conectado. IP:", wifi.ifconfig()[0])
            return True
        sleep(1)
    print("No se pudo conectar al WiFi")
    return False

# ---------- Reloj y CSV ----------
def sincronizar_reloj():
    try:
        ntptime.settime()
        print("Reloj sincronizado.")
    except OSError:
        print("No se pudo sincronizar la hora")

def fecha_hora():
    hora_local = time.time() + ZONA_HORARIA * 3600
    a, m, d, hh, mm, ss, _, _ = time.localtime(hora_local)
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(a, m, d, hh, mm, ss)

def guardar_datos(t, h):
    try:
        with open(NOMBRE_LOCAL, "a") as f:
            f.write(fecha_hora() + ",{:.1f},{:.1f}\n".format(t, h))
    except OSError as e:
        print("Error al escribir archivo:", e)

def leer_csv():
    try:
        with open(NOMBRE_LOCAL, "r") as f:
            return f.read()
    except OSError:
        return ENCABEZADO

def leer_y_vaciar():
    datos = leer_csv()
    with open(NOMBRE_LOCAL, "w") as f:   # buzon vacio para datos nuevos
        f.write(ENCABEZADO)
    return datos

# ---------- GitHub ----------
def enviar_a_github():
    datos = leer_csv()
    if datos.count("\n") <= 1:
        print("CSV vacio, nada que enviar a GitHub")
        return
    contenido_b64 = ubinascii.b2a_base64(datos.encode()).decode().strip()
    url = "https://api.github.com/repos/{}/contents/{}".format(REPO, NOMBRE_LOCAL)
    cabecera = {"Authorization": "token " + GITHUB_TOKEN}
    try:
        resp = urequests.get(url, headers=cabecera)
        sha = resp.json()["sha"] if resp.status_code == 200 else None
        resp.close()
        cuerpo = {"message": "Datos DHT22", "content": contenido_b64}
        if sha is not None:
            cuerpo["sha"] = sha
        resp = urequests.put(url, data=ujson.dumps(cuerpo), headers=cabecera)
        print("GitHub:", "OK" if resp.status_code in (200, 201) else "Error " + str(resp.status_code))
        resp.close()
    except OSError:
        print("GitHub: sin respuesta")

# ---------- Servidor web (puerto 80) ----------
def crear_servidor():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 80))
    s.listen(1)
    s.settimeout(0.5)   # CLAVE: accept se rinde a los 0.5 s y deja trabajar al sensor
    return s

def atender_pedidos(s):
    try:
        conn, direccion = s.accept()
    except OSError:
        return                       # nadie llamo: seguir con el sensor
    print("Pedido de:", direccion)
    try:
        conn.settimeout(2)
        conn.recv(512)
        datos = leer_y_vaciar()
        conn.send("HTTP/1.0 200 OK\r\nContent-Type: text/csv\r\n\r\n")
        conn.sendall(datos.encode())
        print("Enviados {} bytes. Buzon vaciado.".format(len(datos)))
    except OSError:
        print("Fallo al enviar (buzon NO vaciado)")
    conn.close()

# ---------- Arranque ----------
try:
    with open(NOMBRE_LOCAL, "r"):
        pass
except OSError:
    with open(NOMBRE_LOCAL, "w") as f:
        f.write(ENCABEZADO)

if conectar_wifi():
    sincronizar_reloj()
    enviar_a_github()     # enviar lo acumulado mientras estuvo apagado

servidor = crear_servidor()
print("Servidor listo en el puerto 80.")

ultima_lectura = ticks_ms()
ultimo_envio = time.time()
ultimo_intento_wifi = 0

# ---------- Bucle principal: TODO convive aqui ----------
while True:
    try:
        atender_pedidos(servidor)    # atiende la Pi si llama (max 0.5 s)

        # Leer sensor cada 2 segundos
        if ticks_diff(ticks_ms(), ultima_lectura) >= INTERVALO_LECTURA:
            ultima_lectura = ticks_ms()
            try:
                sensor_dht22.measure()
                t = sensor_dht22.temperature()
                h = sensor_dht22.humidity()
                print(fecha_hora(), "| Temp:", t, "| HR:", h)
                guardar_datos(t, h)
            except OSError:
                print("Error data")

        # Subir a GitHub cada hora
        if time.time() - ultimo_envio >= INTERVALO_ENVIO:
            ultimo_envio = time.time()
            if conectar_wifi():
                enviar_a_github()

        # Si el WiFi se cayo, reintentar cada 60 s (sin frenar el resto)
        if not wifi.isconnected() and time.time() - ultimo_intento_wifi >= 60:
            ultimo_intento_wifi = time.time()
            conectar_wifi()

        sleep_ms(50)   # pequena siesta para no ahogar el procesador
    except OSError as e:
        print("Error general:", e)
        sleep_ms(200)

