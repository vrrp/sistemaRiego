import machine
import onewire
import ds18x20
import time
import network
import socket

# ---------- CONFIGURACIÓN ----------
WIFI_SSID = "hertz"
WIFI_PASSWORD = "lilo76980350"
CSV_FILE = "temperaturas.csv"
PIN_SENSOR = 4
INTERVALO_LECTURA = 60  # segundos entre lecturas (ajusta a lo que necesites)

# ---------- WIFI ----------
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Conectado. IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

# ---------- SENSOR ----------
pin = machine.Pin(PIN_SENSOR)
ow = onewire.OneWire(pin)
ds = ds18x20.DS18X20(ow)
roms = ds.scan()

try:
    with open(CSV_FILE, "r") as f:
        pass
except OSError:
    with open(CSV_FILE, "w") as f:
        #f.write("timestamp,temperatura\n")
        f.write("fecha,temperatura\n")

ultima_temp = "N/A"
ultima_lectura = 0

def leer_y_guardar():
    global ultima_temp, ultima_lectura
    if time.time() - ultima_lectura >= INTERVALO_LECTURA:
        ds.convert_temp()
        time.sleep_ms(750)
        for rom in roms:
            temp = ds.read_temp(rom)
            ultima_temp = temp
            t = time.time()
            rtc = machine.RTC()
            fecha=rtc.datetime()
            year = fecha[0]; month = fecha[1]; day = fecha[2]
            hour = fecha[4]; mm   = fecha[5]; ss = fecha[6]
            fechaFormat = str(year)+"-"+str(month)+"-"+str(day)+" "+str(hour)+":"+str(mm)+":"+str(ss)
            with open(CSV_FILE, "a") as f:
                f.write("{},{}\n".format(fechaFormat, temp))
            print("Guardado:", fechaFormat, temp)
        ultima_lectura = time.time()

# ---------- SERVIDOR WEB ----------
def iniciar_servidor(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(5)
    print("Servidor activo en http://{}/".format(ip))

    while True:
        leer_y_guardar()
        s.settimeout(1)  # no bloquear más de 1 seg esperando conexión
        try:
            conn, addr = s.accept()
        except OSError:
            continue  # nadie se conectó, sigue el loop y vuelve a leer sensor

        request = conn.recv(1024).decode()

        if "GET /csv" in request:
            try:
                with open(CSV_FILE, "r") as f:
                    contenido = f.read()
                conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/csv\r\nContent-Disposition: attachment; filename=temperaturas.csv\r\n\r\n")
                conn.send(contenido)
            except:
                conn.send("HTTP/1.1 404 Not Found\r\n\r\n")
        else:
            html = """<!DOCTYPE html>
                        <html>
                        <head><meta charset="UTF-8"><title>Temperatura ESP32</title></head>
                        <body style="font-family: sans-serif; text-align:center; margin-top:50px;">
                        <h1>🌡️ Temperatura Actual</h1>
                        <h2 style="font-size:48px;">{} °C</h2>
                        <p><a href="/csv"><button style="font-size:20px; padding:10px 20px;">📥 Descargar CSV</button></a></p>
                        </body>
                        </html>""".format(ultima_temp)
                                    conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
                                    conn.send(html)
                                    conn.close()

# ---------- MAIN ----------
ip = conectar_wifi()
iniciar_servidor(ip)
