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
import openpyxl


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


if __name__ == '__main__':
    processes = []
    for central in centrales:
        path = r'./ARCHIVOS_REPORTES/'+central.nombre
        if not os.path.exists(path):
            os.mkdir(path)
        path = path + r'/'+current_date_and_time
        if not os.path.exists(path):
            os.mkdir(path)
        print(f'🚀 WORKING WITH {central.nombre}')

        # Crear procesos para ejecutar Axonius y Critical en paralelo
        p1 = multiprocessing.Process(target=run_axonius, args=(central,))
        p2 = multiprocessing.Process(target=run_critical, args=(central,))
        p3 = multiprocessing.Process(target=run_eol,args=(central,))

        processes.extend([p1, p2, p3])

        # Iniciar ambos procesos
        p1.start()
        p2.start()
        p3.start()

    # Esperar a que todos los procesos terminen
    for p in processes:
        p.join()


    print("✅ Todas las consultas y análisis han finalizado.")



    print("📊 Generando reportes!")
    for central in centrales:
        Report(central=central.nombre)
        path_rep = r'./ARCHIVOS_REPORTES/'+central.nombre+ r'/'+current_date_and_time
        path_rep = path_rep + r'/' + f'Reporte_Discovery_{central.nombre}_{current_date_and_time}.xlsx'
        wb = openpyxl.load_workbook(path_rep)
        sheet_reporte = wb[f'Resumen']
        sheet_reporte['A17'].value = f'Servidores {central.nombre} - Vulnerabilidades'
        sheet_reporte['E18'].value = f"=COUNTIF('Inventario'!H6:H1048576,\">0\")"
        sheet_reporte['E19'].value = f"=COUNTIF('Inventario'!I6:I1048576,\">0\")"
        wb.save(path_rep)
        wb.close()
        

    end_time = time.time()  # Captura el tiempo de finalización
    elapsed_time = (end_time - start_time) / 60  # Calcula el tiempo transcurrido
    print(f"⏳ Tiempo de ejecución: {elapsed_time:.2f} minutos")