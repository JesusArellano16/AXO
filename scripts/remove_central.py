# remove_central.py
import os
import sys
from centrales_bk import Central, centrales

scripts_folder = os.path.dirname(os.path.abspath(__file__))

def remove_central(shortName):
    for c in centrales:
        if c.nombre.upper() == shortName.upper():
            centrales.remove(c)
            return c
    return None

def save_to_file(type):
    centrales_file = os.path.join(scripts_folder, f"{type}.py")
    with open(centrales_file, "w", encoding="utf-8") as f:
        f.write("class Central:\n")
        f.write("    def __init__(self, nombre, fullName, queries, file_name):\n")
        f.write("        self.nombre = nombre\n")
        f.write("        self.fullName = fullName\n")
        f.write("        self.queries = queries\n")
        f.write("        self.file_name = file_name\n\n")
        f.write("centrales = [\n")
        for c in centrales:
            f.write("    Central(\n")
            f.write(f'        "{c.nombre}",\n')
            f.write(f'        "{c.fullName}",\n')
            f.write(f"        {c.queries},\n")
            f.write(f"        {c.file_name},\n")
            f.write("    ),\n")
        f.write("]\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Falta el short name de la central a eliminar.")
        sys.exit(1)
    shortName = sys.argv[1].strip().upper()
    removed = remove_central(shortName)

    if removed:
        save_to_file("centrales")
        save_to_file("centrales_bk")
        print("\n✅ Central eliminada correctamente:")
        print(f"- Short name: {removed.nombre}")
        print(f"- Full name: {removed.fullName}")
        print(f"- Centrales restantes: {len(centrales)}")
    else:
        print(f"\n⚠️ No se encontró ninguna central con short name: {shortName}")
