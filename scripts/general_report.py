from pathlib import Path
import shutil
import datetime as dt
from openpyxl import load_workbook
import json
from openpyxl.styles import PatternFill
import urllib3
import warnings
from axonius_api_client import Connect
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter("ignore", category=Warning)

def count_unique_servers(results):
    unique_hosts = set()

    for asset in results:
        hostname = asset.get("specific_data.data.hostname_preferred")
        if hostname:
            unique_hosts.add(hostname.strip().upper())

    return len(unique_hosts)

def fetch_and_count(idx, query_name, devices_api):
    results = devices_api.get_by_saved_query(query_name)
    cantidad_unicos = count_unique_servers(results)
    return idx, cantidad_unicos


def run_general_report(central):
    base_dir = Path(__file__).parent.parent
    today = str(dt.date.today())

    src_file = base_dir / "src" / "Reporte_Discovery.xlsx"

    central_dir = base_dir / "ARCHIVOS_REPORTES" / central
    dated_dir = central_dir / today
    dest_file = dated_dir / f"Reporte_Discovery_{central}_{today}.xlsx"

    # Crear carpeta central si no existe
    central_dir.mkdir(parents=True, exist_ok=True)

    if dated_dir.exists():
        shutil.rmtree(dated_dir)

    dated_dir.mkdir(parents=True, exist_ok=True)

    # Copiar archivo base
    shutil.copy(src_file, dest_file)

    # Abrir Excel
    wb = load_workbook(dest_file)

    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.data_type == "f":  # fórmula
                    cell.value = None       # eliminar fórmula

    ws = wb["Resumen"]

    for row in range(3, 17):
        cell = ws[f"F{row}"]
        cell.value = None
        cell.hyperlink = None

    for row in range(20, 23):
        cell = ws[f"E{row}"]
        cell.value = None
        cell.hyperlink = None

    for sheet_name in wb.sheetnames:
        if sheet_name != "Resumen":
            del wb[sheet_name]

    if central == "GENERAL":
        ws["A2"] = "Inventario - Resumen"
        ws["A19"] = "Servidores - Vulnerabilidades"
    else:
        ws["A2"] = f"Inventario {central} - Resumen"
        ws["A19"] = f"Servidores {central} - Vulnerabilidades"

    red_fill = PatternFill(start_color="FFFF0000", end_color="FFFF0000", fill_type="solid")

    max_col = ws.max_column

    for row in (8, 9):
        for col in range(1, max_col + 1):
            ws.cell(row=row, column=col).fill = red_fill

    assets_count = count_assets_by_central(central)
    ws["F3"] = assets_count
    ws["F4"] = "=F5+F10+F13+F14"
    ws["F7"] = "=F5-F6"
    ws["F12"] = "=F10-F11"
    ws["F16"] = "=F3-F4-F15"

    servers_total, servers_xdr = count_assets_and_xdr(
        central,
        "GENERAL_SERVERS.json"
    )

    ws["F5"] = servers_total
    ws["F6"] = servers_xdr

    pcs_total, pcs_xdr = count_assets_and_xdr(
        central,
        "GENERAL_PCs.json"
    )

    ws["F10"] = pcs_total
    ws["F11"] = pcs_xdr


    ws["F13"] = count_assets_simple(
        central,
        "ALL_GENERAL_NETWORK_DEVICES.json"
    )

    ws["F14"] = count_assets_simple(
        central,
        "GENERAL_VARIOUS_IDENTIFIED_DEVICES.json"
    )

    ws["F15"] = count_assets_simple(
        central,
        "ALL_GENERAL_UNIDENTIFIED_SERVERS.json"
    )
    ws["E20"] = count_assets_simple(
        central,
        "CRITICAL_VULNERABILITIES_GENERAL_SERVERS.json"
    )

    ws["E21"] = count_assets_simple(
        central,
        "HIGH_VULNERABILITIES_GENERAL_SERVERS.json"
    )

    ws["E22"] = count_assets_simple(
        central,
        "EoL_GENERAL_SERVERS.json"
    )
    wb.save(dest_file)

    """if central == "GENERAL":
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

        queries = [
            "HIGH VULNERABILITIES SERVERS IN IXTLAHUACA",
            "CRITICAL VULNERABILITIES SERVERS IN IXTLAHUACA"
        ]

        cell_map = {
            0: "E20",
            1: "E21"
        }

        # --- Ejecutar queries en paralelo ---
        results_map = {}

        with ThreadPoolExecutor(max_workers=len(queries)) as executor:
            futures = [
                executor.submit(fetch_and_count, idx, query, devices_api)
                for idx, query in enumerate(queries)
            ]

            for future in as_completed(futures):
                idx, cantidad_unicos = future.result()
                results_map[idx] = cantidad_unicos

        # --- Escritura en Excel (single-thread) ---
        for idx, cantidad_unicos in results_map.items():
            cell = ws[cell_map[idx]]
            valor_actual = cell.value if isinstance(cell.value, (int, float)) else 0
            cell.value = valor_actual + cantidad_unicos

                """


            

    # Guardar
    wb.save(dest_file)

    return dest_file


def count_assets_by_central(central):
    base_dir = Path(__file__).parent.parent
    general_assets_path = base_dir / "AXONIUS_FILES" / "GENERAL_JSON" / "GENERAL_ASSETS.json"
    unique_labels_path = base_dir / "scripts" / "UNIQUE_LABELS.json"

    with open(general_assets_path, "r", encoding="utf-8") as f:
        assets = json.load(f)

    if central == "GENERAL":
        return len(assets)

    try:
        region_number = int(central.replace("R", ""))
    except ValueError:
        return 0

    with open(unique_labels_path, "r", encoding="utf-8") as f:
        unique_labels = json.load(f)["unique_labels"]

    region_labels = {
        label for label, region in unique_labels.items()
        if region == region_number
    }

    counted_assets = set()

    for asset in assets:
        asset_labels = asset.get("labels", [])
        asset_id = asset.get("internal_axon_id")

        if not asset_id or not isinstance(asset_labels, list):
            continue

        if central == "R9" and "IXTLAHUACA" in asset_labels:
            continue

        # ✅ Contar si tiene AL MENOS un label válido
        if any(label in region_labels for label in asset_labels):
            counted_assets.add(asset_id)

    return len(counted_assets)


def count_assets_and_xdr(central, json_filename):
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / "AXONIUS_FILES" / "GENERAL_JSON" / json_filename
    unique_labels_path = base_dir / "scripts" / "UNIQUE_LABELS.json"

    with open(data_path, "r", encoding="utf-8") as f:
        assets = json.load(f)

    if central == "GENERAL":
        total_assets = set()
        xdr_assets = set()

        for asset in assets:
            asset_id = asset.get("internal_axon_id")
            adapters = asset.get("adapters", [])

            if not asset_id:
                continue

            total_assets.add(asset_id)

            if "paloalto_xdr_adapter" in adapters:
                xdr_assets.add(asset_id)

        return len(total_assets), len(xdr_assets)

    try:
        region_number = int(central.replace("R", ""))
    except ValueError:
        return 0, 0

    with open(unique_labels_path, "r", encoding="utf-8") as f:
        unique_labels = json.load(f)["unique_labels"]

    region_labels = {
        label for label, region in unique_labels.items()
        if region == region_number
    }

    total_assets = set()
    xdr_assets = set()

    for asset in assets:
        asset_id = asset.get("internal_axon_id")
        asset_labels = asset.get("labels", [])
        adapters = asset.get("adapters", [])

        if not asset_id or not isinstance(asset_labels, list):
            continue

        if central == "R9" and "IXTLAHUACA" in asset_labels:
            continue

        if any(label in region_labels for label in asset_labels):
            total_assets.add(asset_id)

            if "paloalto_xdr_adapter" in adapters:
                xdr_assets.add(asset_id)

    return len(total_assets), len(xdr_assets)



def count_assets_simple(central, json_filename):
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / "AXONIUS_FILES" / "GENERAL_JSON" / json_filename
    unique_labels_path = base_dir / "scripts" / "UNIQUE_LABELS.json"

    with open(data_path, "r", encoding="utf-8") as f:
        assets = json.load(f)

    if central == "GENERAL":
        asset_ids = {
            asset.get("internal_axon_id")
            for asset in assets
            if asset.get("internal_axon_id")
        }
        return len(asset_ids)

    try:
        region_number = int(central.replace("R", ""))
    except ValueError:
        return 0

    with open(unique_labels_path, "r", encoding="utf-8") as f:
        unique_labels = json.load(f)["unique_labels"]

    region_labels = {
        label for label, region in unique_labels.items()
        if region == region_number
    }

    counted_assets = set()

    for asset in assets:
        asset_id = asset.get("internal_axon_id")
        asset_labels = asset.get("labels", [])

        if not asset_id or not isinstance(asset_labels, list):
            continue

        if central == "R9" and "IXTLAHUACA" in asset_labels:
            continue

        if any(label in region_labels for label in asset_labels):
            counted_assets.add(asset_id)

    return len(counted_assets)


def main():
    run_general_report("GENERAL")


if __name__ == "__main__":
    main()