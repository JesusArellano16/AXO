import inspect
from axonius_api_client import Connect
import os
from pathlib import Path
from dotenv import load_dotenv
import json

dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Definir credenciales de conexión manualmente
connect_args = {
    "url": os.getenv("AXONIUS_URL"),  # IP de la instancia de Axonius
    "key": os.getenv("AXONIUS_KEY"),  # API Key proporcionada
    "secret": os.getenv("AXONIUS_SECRET"),  # API Secret proporcionado
    "verify": False  # Desactivar la verificación SSL (No recomendado en producción)
}


ax = Connect(**connect_args)

# === FUNCIÓN PARA EXPLORAR ESTRUCTURA ===
def explore(obj, prefix="", depth=1, max_depth=3, lines=None):
    """Explora recursivamente los métodos y submódulos del objeto"""
    if lines is None:
        lines = []
    if depth > max_depth:
        return lines

    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            attr = getattr(obj, name)
            if inspect.ismethod(attr) or inspect.isfunction(attr):
                lines.append(f"{'  ' * depth}- {prefix}{name}()")
            elif not inspect.isbuiltin(attr):
                lines.append(f"{'  ' * depth}+ {prefix}{name}")
                explore(attr, prefix=f"{prefix}{name}.", depth=depth+1, max_depth=max_depth, lines=lines)
        except Exception:
            pass
    return lines


# === EXPLORAR ESTRUCTURA ===
print("🔍 Explorando estructura del cliente Axonius... (esto puede tardar unos segundos)")
lines = explore(ax, max_depth=3)

# === GUARDAR RESULTADOS ===
output_file = "axonius_api_methods.txt"
with open(output_file, "w") as f:
    f.write("=== AXONIUS API CLIENT STRUCTURE ===\n\n")
    f.write("\n".join(lines))

print(f"\n✅ Estructura completa guardada en '{output_file}'")
