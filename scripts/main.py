#from axonius_retreive_data import axonius_retreive_data
from axonius_retreive_data_NEW import axonius_retreive_data
import datetime as dt
#from severities import get_severities
from severities_NEW import get_severities
from dotenv import load_dotenv
#from new_eol import export_eol
from new_eol_NEW import export_eol
import os
from pathlib import Path
from centrales import centrales
import multiprocessing
import time
from report import Report
import shutil
import charts
from queries_general import run_general_json_generation




start_time = time.time()
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




def run_axonius(central):
    #Ejecuta todas las consultas de Axonius en paralelo
    processes = []
    for x in range(len(central.queries)):
        p = multiprocessing.Process(target=axonius_retreive_data, kwargs={
            "connect_args": connect_args,
            "saved_query_name": central.queries[x],
            "saved_query_name_clean": central.file_name[x],
            "central": central.nombre,
            "current_date_and_time": current_date_and_time,
        })
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

def run_critical(central):
    #Ejecuta la función critical en paralelo para las severidades CRITICAL y HIGH
    processes = []
    for severity in ["CRITICAL", "HIGH"]:
        p = multiprocessing.Process(target=get_severities, kwargs={
            "central": central.nombre,
            "f_central": central.fullName,
            "severidad": severity,
        })
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

def run_eol(central):
    #Ejecuta la función critical en paralelo para las severidades CRITICAL y HIGH
    processes = []
    p = multiprocessing.Process(target=export_eol, kwargs={
        "central": central.nombre,
        "f_central": central.fullName,
    })
    processes.append(p)
    p.start()

    for p in processes:
        p.join()


def run_reporte(central):
    processes = []
    p = multiprocessing.Process(target=Report, args=(central,))
    processes.append(p)
    p.start()

    for p in processes:
        p.join()

def only_ixtla_carso_or_both(centrales):
    nombres = {c.nombre for c in centrales}
    return (
        nombres == {"IXTLA"} or
        nombres == {"CARSO"} or
        nombres == {"IXTLA", "CARSO"}
    )

def general_json_done_exists():
    today = str(dt.date.today())
    base_dir = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON"
    done_file = base_dir / f"general_json_{today}.done"
    return done_file.exists()

if __name__ == '__main__':

    if not only_ixtla_carso_or_both(centrales):
        if not general_json_done_exists():
           run_general_json_generation(max_workers=5, delete_previous=True)
    processes = []
    for central in centrales:
        path = r'./ARCHIVOS_REPORTES/'+central.nombre
        if not os.path.exists(path):
            os.mkdir(path)
        path = path + r'/'+current_date_and_time
        if not os.path.exists(path):
            os.mkdir(path)
        path_done = path + r'/done'
        if not os.path.exists(path_done):
            os.mkdir(path_done)

        # Crear procesos para ejecutar Axonius y Critical en paralelo
        p1 = multiprocessing.Process(target=run_axonius, args=(central,))
        p2 = multiprocessing.Process(target=run_critical, args=(central,))
        p3 = multiprocessing.Process(target=run_eol,args=(central,))
        p4 = multiprocessing.Process(target=run_reporte,args=(central,))
        processes.extend([p1, p2, p3, p4])


        # Iniciar ambos procesos
        p1.start()
        p2.start()
        p3.start()
        p4.start()

    # Esperar a que todos los procesos terminen
    for p in processes:
        p.join()
    time.sleep(5)
    for central in centrales:
        try:
            shutil.rmtree(f'./ARCHIVOS_REPORTES/{central.nombre}/{current_date_and_time}/done')
        except Exception as e:
            print(f"⚠️ Error al eliminar {path}: {e}")
    for central in centrales:
        try:
            charts.data_central(central.nombre)
            charts.agregar_hojas_graficas(central.nombre)

        except Exception as e:
            print(f"Error : {e}")
    end_time = time.time()  # Captura el tiempo de finalización
    elapsed_time = (end_time - start_time) / 60  # Calcula el tiempo transcurrido
    print(f"⏳ Tiempo de ejecución: {elapsed_time:.2f} minutos")