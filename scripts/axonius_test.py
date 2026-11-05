import axonius_api_client as axonapi
import json
import os
import urllib3
import warnings
from dotenv import load_dotenv
from pathlib import Path

# ======================================================
# ENV & WARNINGS
# ======================================================
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter("ignore", category=Warning)

connect_args = {
    "url": os.getenv("AXONIUS_URL"),
    "key": os.getenv("AXONIUS_KEY"),
    "secret": os.getenv("AXONIUS_SECRET"),
    "verify": False
}

columns = [
    "adapters",
    "specific_data.data.network_interfaces.ips_preferred",
    "specific_data.data.network_interfaces.mac_preferred",
    "specific_data.data.network_interfaces.manufacturer",
    "Clasificacion"
]

# Carpeta donde viven los JSON generales (misma que usa load_from_json)
GENERAL_JSON_DIR = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON"

# ======================================================
# JSON OFFLINE UTILS
# ======================================================
def load_from_json(json_name, central):
    json_path = GENERAL_JSON_DIR / json_name

    if not json_path.exists():
        raise FileNotFoundError(json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        devices = json.load(f)

    return [d for d in devices if central in d.get("labels", [])]



def download_saved_query_to_json(query_name, json_name, client=None):
    """
    Descarga una Saved Query de Axonius (tal cual, sin filtrar por central ni
    limpiar campos) y la guarda como JSON en GENERAL_JSON_DIR.

    Escribe primero a un archivo temporal y luego reemplaza el definitivo, para
    no dejar un JSON corrupto/vacio si la descarga falla a la mitad.
    Retorna (ruta_json, cantidad_de_dispositivos).
    """
    if client is None:
        client = axonapi.Connect(**connect_args)

    devices = list(client.devices.get_by_saved_query(query_name))

    GENERAL_JSON_DIR.mkdir(parents=True, exist_ok=True)
    json_path = GENERAL_JSON_DIR / json_name
    tmp_path = json_path.with_suffix(json_path.suffix + ".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(devices, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp_path, json_path)

    return json_path, len(devices)


def download_general_tablets():
    """Descarga la Saved Query 'ALL GENERAL TABLETS' a ALL_GENERAL_TABLETS.json"""
    json_path, total = download_saved_query_to_json(
        query_name="ALL GENERAL TABLETS",
        json_name="ALL_GENERAL_TABLETS.json",
    )
    print(f"[OK] {total} dispositivos guardados en {json_path}")
    return json_path


if __name__ == "__main__":
    download_general_tablets()