import os
import json
import shutil
import time
from pathlib import Path
from dotenv import load_dotenv
from axonius_api_client import Connect
import urllib3
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt

# ======================================================
# WARNINGS
# ======================================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter("ignore", category=Warning)

# ======================================================
# FUNCIÓN PRINCIPAL EXPORTABLE
# ======================================================

def run_general_json_generation(
    max_workers: int = 5,
    delete_previous: bool = True
):
    """
    Ejecuta todas las queries generales de Axonius y genera
    un JSON por query en AXONIUS_FILES/GENERAL_JSON.

    Puede ser llamada desde un programa principal.
    """

    start_time = time.time()

    # --------------------------------------------------
    # ENV + CONEXIÓN
    # --------------------------------------------------
    dotenv_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    connect_args = {
        "url": os.getenv("AXONIUS_URL"),
        "key": os.getenv("AXONIUS_KEY"),
        "secret": os.getenv("AXONIUS_SECRET"),
        "verify": False
    }

    ax = Connect(**connect_args)
    devices_api = ax.devices

    # --------------------------------------------------
    # PATHS
    # --------------------------------------------------
    base_dir = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON"

    if delete_previous and base_dir.exists():
        shutil.rmtree(base_dir)

    base_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # QUERIES
    # --------------------------------------------------
    queries = sorted([
        "ALL GENERAL NETWORK DEVICES",
        "ALL GENERAL UNIDENTIFIED SERVERS",
        "CRITICAL VULNERABILITIES GENERAL SERVERS",
        "EoL GENERAL SERVERS",
        "GENERAL ASSETS NO VENDOR",
        "GENERAL IDENTIFIED DEVICES",
        "GENERAL NETWORK DEVICES",
        "GENERAL PCs",
        "GENERAL SERVERS",
        "GENERAL UNMANAGED ASSESTS",
        "GENERAL VARIOUS IDENTIFIED",
        "HIGH VULNERABILITIES GENERAL SERVERS",
    ])

    # --------------------------------------------------
    # WORKER
    # --------------------------------------------------
    def run_query(query_name: str):
        try:
            results = devices_api.get_by_saved_query(query_name)
            output_file = base_dir / f"{query_name.replace(' ', '_')}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)

            return query_name, len(results) if results else 0, None

        except Exception as e:
            return query_name, 0, str(e)

    # --------------------------------------------------
    # EJECUCIÓN EN PARALELO
    # --------------------------------------------------
    results_summary = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_query, q) for q in queries]

        for future in as_completed(futures):
            query_name, total, error = future.result()
            results_summary[query_name] = {
                "total": total,
                "error": error
            }

            if error:
                print(f"✖ {query_name} | ERROR | {error}")
            else:
                print(f"✔ {query_name} | {total} elementos")

    elapsed_minutes = round((time.time() - start_time) / 60, 2)

    print(f"\n⏱ Proceso completo en {elapsed_minutes} minutos")
    today = str(dt.date.today())
    done = base_dir / f"general_json_{today}.done"
    with open(done,"w") as f:
        f.write("done")

    return results_summary
