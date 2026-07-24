
import os
import subprocess as cmd
import datetime as dt


path_now = os.getcwd()
#path_project = path_now+"/vrrp.github.io"
#path_img = "/home/proyectos/pyprojects/coronavirus2020_api/"

#os.chdir(path_project)

time = dt.datetime.now()
date = time.strftime("%d-%B-%Y")
times= time.strftime("%H:%M:%S")
mensaje = times+" "+date
#year = date.year; month=date.month; day=date.day

os.system("git pull origin main")

