import os
import sys
import importlib.util
import shutil

scripts_folder = os.path.dirname(os.path.abspath(__file__))
centrales_file = os.path.join(scripts_folder, f"centrales.py")
centrales_bk_file = os.path.join(scripts_folder, f"centrales_bk.py")



def cargar_centrales():
    """Importa dinámicamente el archivo centrales.py y retorna la lista de centrales."""
    spec = importlib.util.spec_from_file_location("centrales", centrales_bk_file)
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
