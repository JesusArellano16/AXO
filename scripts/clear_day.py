import sys
import os
import shutil
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        sys.exit("No se proporcionaron centrales a limpiar.")

    centrales = sys.argv[1:]  # todos los argumentos excepto el nombre del script

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reportes_dir_base = os.path.join(base_dir, "ARCHIVOS_REPORTES")
    today = datetime.now().strftime("%Y-%m-%d")

    for central in centrales:
        target_dir = os.path.join(reportes_dir_base, central, today)
        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
                print(f"Carpeta eliminada: {target_dir}")
            except Exception as e:
                print(f"Error al eliminar {target_dir}: {e}")
        else:
            print(f"No existe la carpeta: {target_dir}")

if __name__ == "__main__":
    main()
