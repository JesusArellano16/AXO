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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter("ignore", category=Warning)

def timestamp():
    return dt.datetime.now().strftime("%H:%M:%S.%f")[:-3]

def backup_json_files(base_dir: Path):
    today = str(dt.date.today())

    dest_dir = (
        base_dir.parent.parent
        / "RECORD"
        / "GENERAL_JSON"
        / today
    )

    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    dest_dir.mkdir(parents=True, exist_ok=True)

    for file in base_dir.glob("*.json"):
        shutil.copy2(file, dest_dir / file.name)

    print(f"[{timestamp()}] Backup creado en: {dest_dir}")

def run_general_json_generation(
    max_workers: int = 10,
    delete_previous: bool = True
):
    results_summary = {}
    has_error = False
    start_time = time.time()

    dotenv_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    connect_args = {
        "url": os.getenv("AXONIUS_URL"),
        "key": os.getenv("AXONIUS_KEY"),
        "secret": os.getenv("AXONIUS_SECRET"),
        "verify": False,
    }

    ax = Connect(**connect_args)

    base_dir = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON"

    if delete_previous and base_dir.exists():
        shutil.rmtree(base_dir)

    base_dir.mkdir(parents=True, exist_ok=True)

    queries = [ "HIGH VULNERABILITIES GENERAL SERVERS", 
               "EoL GENERAL SERVERS", 
               "CRITICAL VULNERABILITIES GENERAL SERVERS", 
               "GENERAL ASSETS", 
               "ALL GENERAL NETWORK DEVICES", 
               "ALL GENERAL UNIDENTIFIED SERVERS", 
               "GENERAL IDENTIFIED DEVICES", 
               "GENERAL PCs", 
               "GENERAL SERVERS", 
               "GENERAL VARIOUS IDENTIFIED DEVICES", ]

    def get_with_retry(api, query_name, page_size, offset, retries=5):
        for attempt in range(retries):
            try:
                return api.get_by_saved_query(
                    query_name,
                    page_size=page_size,
                    offset=offset,
                )
            except Exception as e:
                print(f"[{timestamp()}] Retry {attempt+1} offset {offset}")
                time.sleep(3)

        raise Exception(f"Falló definitivamente en offset {offset}")

    def run_query(query_name: str):
        try:
            start_query = time.perf_counter()

            ax_local = Connect(**connect_args)
            #print(f"[{timestamp()}] EMPEZAMOS {query_name}")

            devices_api_local = ax_local.devices
            output_file = base_dir / f"{query_name.replace(' ', '_')}.json"

            if query_name == "HIGH VULNERABILITIES GENERAL SERVERS":

                page_size = 1000
                offset = 0
                total_written = 0

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("[\n")
                    first_item = True

                    while True:
                        batch = get_with_retry(
                            devices_api_local,
                            query_name,
                            page_size,
                            offset,
                        )

                        if not batch:
                            break

                        for item in batch:
                            if not first_item:
                                f.write(",\n")
                            json.dump(item, f, ensure_ascii=False)
                            first_item = False
                            total_written += 1

                        print(
                            f"[{timestamp()}] HIGH descargados: {total_written}"
                        )

                        break

                    f.write("\n]")

                end_query = time.perf_counter()
                duration = round(end_query - start_query, 2)

                #print(f"[{timestamp()}] TERMINAMOS {query_name} | ⏱ {duration} segundos TOTAL")

                return query_name, total_written, None


            else:
                results = devices_api_local.get_by_saved_query(query_name)

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)

                end_query = time.perf_counter()
                duration = round(end_query - start_query, 2)

                #print(f"[{timestamp()}] TERMINAMOS {query_name} | ⏱ {duration} segundos TOTAL")

                return query_name, len(results) if results else 0, None

        except Exception as e:
            error_msg = str(e)
            if "Falló definitivamente" in error_msg:
                return query_name, 0, "ERROR_EN_RED"

            return query_name, 0, error_msg

    results_summary = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_query, q) for q in queries]

        for future in as_completed(futures):
            query_name, total, error = future.result()
            results_summary[query_name] = {
                "total": total,
                "error": error,
            }

            if error:
                print(f"✖ {query_name} | ERROR | {error}")
                if error == "ERROR_EN_RED":
                    has_error = True
            else:
                print(f"✔ {query_name} | {total} elementos")

    elapsed_minutes = round((time.time() - start_time) / 60, 2)

    print(f"\n⏱ Proceso completo en {elapsed_minutes} minutos")

    today = str(dt.date.today())
    done = base_dir / f"general_json_{today}.done"

    with open(done, "w") as f:
        f.write("done")
    backup_json_files(base_dir)
    return {
        "results": results_summary,
        "success": not has_error
        }
