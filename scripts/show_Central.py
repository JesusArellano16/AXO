# list_centrals.py
from centrales import centrales

def list_central_names():
    if not centrales:
        print("⚠️ No hay centrales registradas.")
        return

    print("📋 Centrals:\n")
    for c in centrales:
        print(f"- {c.nombre}")

if __name__ == "__main__":
    list_central_names()
