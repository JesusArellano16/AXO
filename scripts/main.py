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

def verificar_archivo(vuln,central):
    # Ruta de la carpeta donde debe estar
    ruta_base = "AXONIUS_FILES"
    ruta_completa = os.path.join(ruta_base, central)

    # Verificar si la carpeta central existe
    if not os.path.isdir(ruta_completa):
        return False  # La carpeta no existe

    # Verificar si el archivo "vuln.csv" está dentro de central
    return f"{vuln}.csv" in os.listdir(ruta_completa)

for central in centrales:
    print(f'🚀 WORKING WITH {central.nombre}')
    for x in range (0,len(central.queries)):
        #Aquí meteremos los networks y assets
        axonius_retreive_data(
            connect_args = connect_args,
            saved_query_name = central.queries[x],
            saved_query_name_clean = central.file_name[x],
            central = central.nombre,
            current_date_and_time = current_date_and_time,
            ) 
    if verificar_archivo(vuln="critical",central=central.nombre):
        print(f'🚀 {central.nombre} has critical vulnerabilities')
        critical(central=central.nombre,current_date_and_time=current_date_and_time,severidad="CRITICAL")

    if verificar_archivo(vuln="high",central=central.nombre):
        print(f'🚀 {central.nombre} has high vulnerabilities')
        critical(central=central.nombre,current_date_and_time=current_date_and_time,severidad="HIGH")
    print(f'✅{central.nombre} created')
        



print("------------------------------------------")
print("------------------------------------------")
print("------------------------------------------")
print("-------RECUERDA LLENAR EL REPORTE---------")
print("------------------------------------------")
print("------------------------------------------")
print("------------------------------------------")
