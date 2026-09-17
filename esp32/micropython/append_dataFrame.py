import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

pathDataBase = "/home/projects/sistemaRiego/dataBase/"
os.chdir(pathDataBase)

archivos = ["database_aws01.csv", "datos_met.csv"]


df_completo = pd.concat([pd.read_csv(f) for f in archivos], ignore_index=True)

df_completo["fecha_hora"] = pd.to_datetime(df_completo["fecha_hora"])

df_completo = df_completo.sort_values(by="fecha_hora", ascending=True)

#plt.plot(df_completo["fecha_hora"], df_completo["humedad"], 'bo-')
#plt.show()

df_completo.to_csv("database_aws01.csv", index=False)
