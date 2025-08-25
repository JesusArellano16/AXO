from axonius_retreive_data import axonius_retreive_data
import datetime as dt
from critical import critical
from dotenv import load_dotenv
from eol import Eol
import os
from pathlib import Path
from centrales import centrales
import multiprocessing
import time
from report import Report
import shutil
import charts
import sys
import importlib.util

scripts_folder = os.path.dirname(os.path.abspath(__file__))
centrales_file = os.path.join(scripts_folder, f"centrales.py")
centrales_bk_file = os.path.join(scripts_folder, f"centrales_bk.py")



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
        p = multiprocessing.Process(target=critical, kwargs={
            "central": central.nombre,
            "current_date_and_time": current_date_and_time,
            "severidad": severity,
        })
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

def run_eol(central):
    #Ejecuta la función critical en paralelo para las severidades CRITICAL y HIGH
    processes = []
    p = multiprocessing.Process(target=Eol, kwargs={
        "central": central.nombre,
        "current_date_and_time": current_date_and_time,
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

def cargar_centrales():
    """Importa dinámicamente el archivo centrales.py y retorna la lista de centrales."""
    spec = importlib.util.spec_from_file_location("centrales", centrales_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Central, mod.centrales

def guardar_centrales(Central, centrales_filtradas):
    """Reescribe el archivo centrales.py con solo las centrales filtradas."""
    with open(centrales_file, "w") as f:
        f.write("class Central:\n")
        f.write("    def __init__(self, nombre, fullName, queries, file_name):\n")
        f.write("        self.nombre = nombre\n")
        f.write("        self.fullName = fullName\n")
        f.write("        self.queries = queries\n")
        f.write("        self.file_name = file_name\n\n")

        f.write("centrales = [\n")
        for c in centrales_filtradas:
            f.write(f"    Central(\n")
            f.write(f"        \"{c.nombre}\",\n")
            f.write(f"        \"{c.fullName}\",\n")
            f.write(f"        {c.queries},\n")
            f.write(f"        {c.file_name},\n")
            f.write("    ),\n")
        f.write("]\n")

if __name__ == '__main__':

    nombres_permitidos = sys.argv[1:]
    Central_aux, centrales_aux = cargar_centrales()
    centrales_filtradas = [c for c in centrales_aux if c.nombre in nombres_permitidos]
    if not centrales_filtradas:
        print("⚠️ Ninguna central coincide con los parámetros dados.")
        sys.exit(1)
    guardar_centrales(Central_aux, centrales_filtradas)

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
            #charts.servers(central.nombre)
            #charts.servers_cortex(central.nombre)
            #charts.agregar_hojas_graficas(central.nombre)
        except Exception as e:
            print(f"Error : {e}")
    end_time = time.time()  # Captura el tiempo de finalización
    elapsed_time = (end_time - start_time) / 60  # Calcula el tiempo transcurrido
    print(f"⏳ Tiempo de ejecución: {elapsed_time:.2f} minutos")
    shutil.copy(centrales_bk_file, centrales_file)