from axonius_retreive_data import axonius_retreive_data
import datetime as dt
from critical import critical
from dotenv import load_dotenv
import os
from pathlib import Path
from centrales import centrales

dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Definir credenciales de conexión manualmente
connect_args = {
    "url": os.getenv("AXONIUS_URL"),  # IP de la instancia de Axonius
    "key": os.getenv("AXONIUS_KEY"),  # API Key proporcionada
    "secret": os.getenv("AXONIUS_SECRET"),  # API Secret proporcionado
    "verify": False  # Desactivar la verificación SSL (No recomendado en producción)
}

current_date_and_time = str(dt.date.today())


for central in centrales:
    for x in range (0,len(central.queries)):
        #Aquí meteremos los networks y assets
        axonius_retreive_data(
            connect_args = connect_args,
            saved_query_name = central.queries[x],
            saved_query_name_clean = central.file_name[x],
            central = central.nombre,
            current_date_and_time = current_date_and_time,
            )




print("------------------------------------------")
print("------------------------------------------")
print("------------------------------------------")
print("-------RECUERDA LLENAR EL REPORTE---------")
print("------------------------------------------")
print("------------------------------------------")
print("------------------------------------------")
