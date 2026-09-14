import os

"""
En Raspberry Pi 3 B+:
    http://IP_DEL_ESP32:8266
    
    E valor de IP_DEL_ESP32 la imprime el scritp al conectar
    al wife: 192.168.1.91
    
    
Arquitectura ESP32:
    ROM (fabrica)			: 448 KB
    RAM (trabajo)			: 520 KB (free 100 KB)
    RTC RAM (despertador)	: 16-24 KB
    FLASH (almacen)			: 4-16 MB
    
Particiones del FLASH:
    nvs			: 24 KB
    phy_init 	: 4 KB
    factory		: 16-1.9 MB : esel cerebro, micropython
    vfs 		: 1.5-2 MB	: sstema de archivo: boot.py,main.py, etc.

Acceder a la particion vfs desde la Pi
    Actualizar e instalar en la Pi
        $ sudo apt update
        $ sudo apt install pipx

        $ pipx install mpremote
        $ pipx ensurepath
        $ mpremote --version

    instalar
        $ pip install mpremote

    listar archivos de vfs
        $ mpremote connect /dev/ttyUSB0 fs ls

    Extraer archivos del esp32 hacia la Pi
        $ mpremote connect /dev/ttyUSB0 fs cp :datos_met.csv ./dataBase/datos_met.csv

"""

pathDir = os.getcwd()
pathDataBase = "/home/projects/sistemaRiego/dataBase/"
print(pathDir)

os.chdir(pathDataBase)
os.system("mpremote connect /dev/ttyUSB0 fs cp :datos_met.csv ./datos_met.csv")
os.system("mpremote --version")

dataFile = "datos_met.csv"
sizeDataFile_Bytes = os.path.getsize(pathDataBase+dataFile)
sizeKB = round(sizeDataFile_Bytes/1024, 1)
sizeMB = round(sizeKB/1024, 1)
print(f"{sizeDataFile_Bytes} Bytes, {sizeKB} KB")

if os.path.exists(pathDataBase+dataFile):
    if sizeMB>=1.5:
        print("Queda poco espacio, liberar espacio en particion vfs")

    else:
        print("Hay pocos datos")

else:
    print("datos_met.csv no esta en la ruta de la Pi")

#print(os.listdir())
#print(os.statvfs("/")) # indica el espacio libre del directorio
