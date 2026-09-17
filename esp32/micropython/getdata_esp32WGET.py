import os
"""
ip esp32 wifi-home
192.168.1.91
"""
pathDir = os.getcwd()
pathDataBase = "/home/projects/sistemaRiego/dataBase"


os.chdir(pathDataBase)
os.system("wget http://192.168.1.91/datos_met.csv -O datos_met.csv")
#os.system("curl http://192.168.1.91/datos_met.csv -O datos_met.csv")

