import os
import json
import urllib3
import requests
from pathlib import Path
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CHART_ID = "69c674a1c08bd4c8676c625e"
OUTPUT_DIR = Path(__file__).parent / "AXONIUS_FILES" / "GENERAL_JSON"
OUTPUT_FILE = OUTPUT_DIR / "AX_TEST_DEVICES_REPORT.json"

def main():
    load_dotenv()

    url = os.getenv("AXONIUS_URL")
    key = os.getenv("AXONIUS_KEY")
    secret = os.getenv("AXONIUS_SECRET")

    headers = {
        "accept": "application/json",
        "api-key": key,
        "api-secret": secret
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_data = []
    page = 1
    page_size = 200  # 🔥 sube esto (prueba 200–1000 según performance)

    print(f"[*] Consultando chart ID: {CHART_ID}")

    while True:
        full_url = f"{url}/api/v2/dashboards/charts/{CHART_ID}?page={page}&page_size={page_size}"

        response = requests.get(full_url, headers=headers, verify=False)

        if response.status_code != 200:
            print(f"[!] Error {response.status_code}: {response.text}")
            return

        data = response.json()

        # 🔥 AJUSTA ESTO SEGÚN ESTRUCTURA REAL
        results = data.get("data", [])

        if not results:
            print("[*] No más datos, terminamos")
            break

        all_data.extend(results)

        print(f"[+] Página {page} -> {len(results)} registros")

        # si vienen menos que page_size → última página
        if len(results) < page_size:
            break

        page += 1

    # guardar todo
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"[+] JSON generado: {OUTPUT_FILE}")
    print(f"[+] Total de registros: {len(all_data)}")

if __name__ == "__main__":
    main()