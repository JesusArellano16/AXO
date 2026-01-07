import os
import json
import warnings
import urllib3
from pathlib import Path
import axonius_api_client as axonapi
from dotenv import load_dotenv
from axonius_api_client.constants.fields import UnknownFieldSchema

# ======================================================
# WARNINGS OFF
# ======================================================
warnings.filterwarnings("ignore", category=axonapi.exceptions.ExtraAttributeWarning)
warnings.filterwarnings("ignore", category=UnknownFieldSchema)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ======================================================
# CONFIG
# ======================================================
SAVED_QUERY_NAME = "PCs IN CARSO LEGACY"
OUTPUT_DIR = Path(__file__).parent / "AXONIUS_FILES" / "GENERAL_JSON"
OUTPUT_FILE = OUTPUT_DIR / "PCs_IN_CARSO_LEGACY.json"

# ======================================================
# MAIN
# ======================================================
def main():
    load_dotenv()

    connect_args = {
        "url": os.getenv("AXONIUS_URL"),
        "key": os.getenv("AXONIUS_KEY"),
        "secret": os.getenv("AXONIUS_SECRET"),
        "verify": False
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    client = axonapi.Connect(**connect_args)

    print(f"[*] Ejecutando saved query: {SAVED_QUERY_NAME}")
    devices = client.devices.get_by_saved_query(SAVED_QUERY_NAME)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=2, ensure_ascii=False)

    print(f"[+] JSON generado: {OUTPUT_FILE}")
    print(f"[+] Total de assets: {len(devices)}")

if __name__ == "__main__":
    main()
