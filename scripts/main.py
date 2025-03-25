from servidores import servers
from networks import networks
from pcs import pcs
import datetime as dt
from critical import critical
import os

current_date_and_time = str(dt.date.today())
central = input("¿Que central estás trabajando? ").upper()
path = r'./ARCHIVOS_REPORTES/'+central
if not os.path.exists(path):
    os.mkdir(path)
path = path + r'/'+current_date_and_time
if not os.path.exists(path):
    os.mkdir(path)
servers(central, current_date_and_time)
pcs(central, current_date_and_time)
networks(central, current_date_and_time)
a = input("La central tiene vulneravilidades? (si/no)").upper()
if a=="SI":
    critical(central, current_date_and_time,"critical")
    critical(central, current_date_and_time,"high")
print("------------------------------------------")
print("------------------------------------------")
print("------------------------------------------")
print("-------RECUERDA LLENAR EL REPORTE---------")
print("------------------------------------------")
print("------------------------------------------")
print("------------------------------------------")
