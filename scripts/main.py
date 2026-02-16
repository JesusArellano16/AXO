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
from general_report import run_general_report


start_time = time.time()

multiprocessing.set_start_method("spawn", force=True)

dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

connect_args = {
    "url": os.getenv("AXONIUS_URL"),
    "key": os.getenv("AXONIUS_KEY"),
    "secret": os.getenv("AXONIUS_SECRET"),
    "verify": False
}

current_date_and_time = str(dt.date.today())



def run_all_queries_for_central(central):
    processes = []

    # -----------------------------
    # 1️⃣ AXONIUS (4 queries)
    # -----------------------------
    for query, filename in zip(central.queries, central.file_name):
        p = multiprocessing.Process(
            target=axonius_retreive_data,
            kwargs={
                "connect_args": connect_args,
                "saved_query_name": query,
                "saved_query_name_clean": filename,
                "central": central.nombre,
                "current_date_and_time": current_date_and_time,
            }
        )
        processes.append(p)
        p.start()

    # -----------------------------
    # 2️⃣ SEVERITIES (2 queries)
    # -----------------------------
    for severity in ["CRITICAL", "HIGH"]:
        p = multiprocessing.Process(
            target=get_severities,
            kwargs={
                "central": central.nombre,
                "f_central": central.fullName,
                "severidad": severity,
            }
        )
        processes.append(p)
        p.start()

    # -----------------------------
    # 3️⃣ EOL (1 query)
    # -----------------------------
    p = multiprocessing.Process(
        target=export_eol,
        kwargs={
            "central": central.nombre,
            "f_central": central.fullName,
        }
    )
    processes.append(p)
    p.start()

    # -----------------------------
    # Esperar a que los 7 terminen
    # -----------------------------
    for p in processes:
        p.join()


def run_reporte(central):
    p = multiprocessing.Process(target=Report, args=(central,))
    p.start()
    p.join()



def only_ixtla_carso_or_both(centrales):
    nombres = {c.nombre for c in centrales}
    return nombres == {"IXTLA"}


def general_json_done_exists():
    today = str(dt.date.today())
    base_dir = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON"
    done_file = base_dir / f"general_json_{today}.done"
    return done_file.exists()



if __name__ == '__main__':

    if not only_ixtla_carso_or_both(centrales):
        if not general_json_done_exists():
            run_general_json_generation(max_workers=10, delete_previous=True)
            """
            time.sleep(5)
            exit()
            """
            

    GENERAL_REPORT_CENTRALS = {f"R{i}" for i in range(1, 10)} | {"GENERAL"}

    for central in centrales:
        path = f'./ARCHIVOS_REPORTES/{central.nombre}/{current_date_and_time}/done'
        os.makedirs(path, exist_ok=True)
        if central.nombre in GENERAL_REPORT_CENTRALS:
            run_general_report(central.nombre)
        
        else:
            run_all_queries_for_central(central)

            run_reporte(central)


    time.sleep(5)

    for central in centrales:
        if central.nombre in GENERAL_REPORT_CENTRALS:
            run_general_report(central.nombre)
        
        else:
            try:
                shutil.rmtree(f'./ARCHIVOS_REPORTES/{central.nombre}/{current_date_and_time}/done')
            except Exception as e:
                print(f"⚠️ Error al eliminar carpeta done: {e}")

    for central in centrales:
        if central.nombre in GENERAL_REPORT_CENTRALS:
            run_general_report(central.nombre)
        
        else:
            try:
                charts.data_central(central.nombre)
                charts.agregar_hojas_graficas(central.nombre)
            except Exception as e:
                print(f"Error generando gráficas: {e}")

    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60

    print(f"\nTiempo de ejecución: {elapsed_time:.2f} minutos")
