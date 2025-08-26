# remove_central.py
import os
from centrales_bk import Central, centrales

scripts_folder = os.path.dirname(os.path.abspath(__file__))

def remove_central(fullName):
    for c in centrales:
        if c.fullName.upper() == fullName.upper():  # case-insensitive match
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
    fullName = input("👉 Enter the full name of the central to remove: ").strip().upper()
    removed = remove_central(fullName)

    if removed:
        save_to_file("centrales")
        save_to_file("centrales_bk")
        print("\n✅ Central successfully removed:")
        print(f"- Short name: {removed.nombre}")
        print(f"- Full name: {removed.fullName}")
        print(f"- Remaining centrals: {len(centrales)}")
    else:
        print("\n⚠️ No central found with that full name.")
