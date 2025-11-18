from axonius_api_client import Connect
import os
from pathlib import Path
from dotenv import load_dotenv
import json
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from collections import defaultdict
import datetime as dt
import warnings, axonius_api_client




warnings.filterwarnings(action="ignore", category=axonius_api_client.exceptions.ExtraAttributeWarning)
warnings.filterwarnings("ignore")
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Definir credenciales de conexión manualmente
connect_args = {
    "url": os.getenv("AXONIUS_URL"),  # IP de la instancia de Axonius
    "key": os.getenv("AXONIUS_KEY"),  # API Key proporcionada
    "secret": os.getenv("AXONIUS_SECRET"),  # API Secret proporcionado
    "verify": False  # Desactivar la verificación SSL (No recomendado en producción)
}


#ax = Connect(**connect_args)


"""
adapter_name = "cisco_apic"  # Nombre del adaptador Cisco

print(f"🔍 Listando conexiones existentes para '{adapter_name}'...\n")

# Obtener todas las conexiones de ese adaptador
connections = ax.adapters.cnx.get_by_adapter(adapter_name)

# Mostrar en consola y guardar en JSON
print(json.dumps(connections, indent=4))

output_file = f"{adapter_name}_connections.json"
with open(output_file, "w") as f:
    json.dump(connections, f, indent=4)

print(f"\n💾 Conexiones guardadas en '{output_file}'")
"""