# add_central.py
import os
from centrales_bk import Central, centrales
import shutil

scripts_folder = os.path.dirname(os.path.abspath(__file__))
#centrales_file = os.path.join(scripts_folder, "centrales.py")
desarrollo_folder = os.path.dirname(scripts_folder)
base_path = os.path.join(desarrollo_folder, "AXONIUS_FILES")
data_path = os.path.join(desarrollo_folder,"src")

def add_central(name, fullName):
    queries = [
        f"ASSETS IN {fullName}",
        f"SERVERS IN {fullName}",
        f"ALL NETWORK DEVICES IN {fullName}",
        f"PCs IN {fullName}"
    ]

    file_names = [
        "TOTAL_ASSETS",
        "SERVERS",
        "NET_DEV",
        "PCs"
    ]

    new_central = Central(name, fullName, queries, file_names)
    centrales.append(new_central)
    return new_central

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

def create_central_folder(name):
    folder_path = os.path.join(base_path, name)
    os.makedirs(folder_path, exist_ok=True)  # crea la carpeta si no existe

    src_file = os.path.join(data_path, "data.csv")
    graficas_folder = os.path.join(data_path, "Graficas")
    os.makedirs(graficas_folder, exist_ok=True)
    dest_file = os.path.join(graficas_folder, f"data_{name}.csv")
    shutil.copyfile(src_file, dest_file)
    return 

if __name__ == "__main__":
    name = input("👉 Enter short name (e.g. L_ARA): ").strip().upper()
    fullName = input("👉 Enter full name (e.g. LAGO ARAGON): ").strip().upper()

    new_central = add_central(name, fullName)
    save_to_file("centrales")
    save_to_file("centrales_bk")
    create_central_folder(name)

    print("\n✅ Central permanently added to centrales.py:")
    print(f"- Short name: {new_central.nombre}")
    print(f"- Full name: {new_central.fullName}")
