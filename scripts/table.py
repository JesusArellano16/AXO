from rich.table import Table
from rich.console import Console
import time
import os

def limpiar_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def archivo_existe(path, nombre):
    archivo = f"{path}/done/{nombre}"
    return os.path.exists(archivo)

def mostrar_tabla(centrales, current_date_and_time):
    console = Console()
    table = Table(title="Estado de generación de archivos", show_lines=True)

    table.add_column("Archivo", justify="left")
    for central in centrales:
        table.add_column(central.nombre, justify="center")

    nombres_archivos = ["critical", "high", "eol", "NET_DEV", "PCs", "SERVERS", "TOTAL_ASSETS","Reporte"]

    # Limpiar la terminal antes de mostrar la tabla
    limpiar_terminal()

    # Mostrar la tabla
    for archivo in nombres_archivos:
        row = [archivo]
        for central in centrales:
            path_base = f"./ARCHIVOS_REPORTES/{central.nombre}/{current_date_and_time}"
            nombre_arch = f"{archivo}_{central.nombre}.done"
            existe = archivo_existe(path_base, nombre_arch)
            row.append("✅" if existe else "🚀")
        table.add_row(*row)

    console.print(table)

""" 
    # Verificar si todos los archivos .done existen
    todos_listos = all(
        archivo_existe(f"./ARCHIVOS_REPORTES/{central.nombre}/{current_date_and_time}", f"{archivo}_{central.nombre}.done")
        for central in centrales
        for archivo in nombres_archivos
    )

    if todos_listos:
        console.print("\n🎉 Todos los archivos han sido generados correctamente.\n", style="bold green")
    else:
        time.sleep(1)
        mostrar_tabla(centrales, current_date_and_time) """