from machine import Pin
from utime import sleep
import dht

sensor_dht22 = dht.DHT22(Pin(13))

while True:
    try:
        sensor_dht22.measure()
        t = sensor_dht22.temperature()
        h = sensor_dht22.humidity()
        
        print("Temp :", t)
        print("HR : ",  h)
        sleep(2)
        print("")
        
    except OSError as e:
        print("Error data")
