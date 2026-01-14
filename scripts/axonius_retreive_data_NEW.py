import os
import json
import warnings
import urllib3
import pandas as pd
import openpyxl
from openpyxl.styles import Alignment
from pathlib import Path
import datetime as dt
import axonius_api_client as axonapi
from dotenv import load_dotenv
from axonius_api_client.constants.fields import UnknownFieldSchema

# ======================================================
# WARNINGS OFF
# ======================================================
warnings.filterwarnings("ignore", category=axonapi.exceptions.ExtraAttributeWarning)
warnings.filterwarnings("ignore", category=UnknownFieldSchema)
warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ======================================================
# FECHA GLOBAL
# ======================================================
current_date_and_time = str(dt.date.today())

# ======================================================
# JSON OFFLINE UTILITIES
# ======================================================

def normalize_multivalue(value):
    """
    Convierte listas en texto multilínea para Excel
    """
    if isinstance(value, list):
        return "\n".join(str(v) for v in value if v is not None)
    return value

def resolve_json_from_query(saved_query_name: str):
    q = saved_query_name.upper()

    if "SERVERS" in q:
        return "GENERAL_SERVERS.json"
    if "NETWORK DEVICES" in q:
        return "ALL_GENERAL_NETWORK_DEVICES.json"
    if "PCS" in q:
        return "GENERAL_PCs.json"


    raise ValueError(f"No mapping for query: {saved_query_name}")


def load_devices_from_json(saved_query_name, central):
    base_dir = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON"
    json_file = resolve_json_from_query(saved_query_name)
    json_path = base_dir / json_file

    if not json_path.exists():
        raise FileNotFoundError(json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        devices = json.load(f)

    # Filtrar por label
    return [d for d in devices if central in d.get("labels", [])]


# ======================================================
# FUNCIÓN PRINCIPAL
# ======================================================

def axonius_retreive_data(
    connect_args,
    saved_query_name,
    saved_query_name_clean,
    central,
    current_date_and_time
):
    # --------------------------------------------------
    # PATHS
    # --------------------------------------------------
    base_path = f'./ARCHIVOS_REPORTES/{central}/{current_date_and_time}'
    os.makedirs(f'{base_path}/done', exist_ok=True)

    from table import mostrar_tabla
    from centrales import centrales
    mostrar_tabla(centrales, current_date_and_time)

    # --------------------------------------------------
    # DATA SOURCE RULE
    # --------------------------------------------------
    use_api = (central == "IXTLA") or (saved_query_name_clean == "TOTAL_ASSETS")

    if use_api:
        client = axonapi.Connect(**connect_args)
        devices = client.devices.get_by_saved_query(saved_query_name)
    else:
        devices = load_devices_from_json(saved_query_name, central)

    # --------------------------------------------------
    # LIMPIEZA
    # --------------------------------------------------
    clean_devices = []

    if saved_query_name_clean == "NET_DEV":
        fields = [
            "adapters",
            "specific_data.data.hostname_preferred",
            "specific_data.data.network_interfaces.ips_preferred",
            "specific_data.data.network_interfaces.mac_preferred",
            "specific_data.data.os.type_distribution_preferred",
            "specific_data.data.network_interfaces.manufacturer"
        ]
    else:
        fields = [
            "adapters",
            "specific_data.data.hostname_preferred",
            "specific_data.data.network_interfaces.ips_preferred",
            "specific_data.data.network_interfaces.mac_preferred",
            "specific_data.data.os.type_distribution_preferred"
        ]

    for device in devices:
        d = {}
        for f in fields:
            if f in device:
                d[f] = normalize_multivalue(device[f])

        if saved_query_name_clean != "NET_DEV":
            d["CORTEX"] = "SI" if "paloalto_xdr_adapter" in d.get("adapters", []) else "NO"
            d["VIRTUAL PATCHING"] = "SI" if "deep_security_adapter" in d.get("adapters", []) else "NO"

        clean_devices.append(d)

    # --------------------------------------------------
    # EXCEL
    # --------------------------------------------------
    df = pd.DataFrame(clean_devices)

    headers = {
        "adapters": "Adapter",
        "specific_data.data.hostname_preferred": "Hostname",
        "specific_data.data.network_interfaces.ips_preferred": "IPs",
        "specific_data.data.network_interfaces.mac_preferred": "MAC",
        "specific_data.data.os.type_distribution_preferred": "OS",
        "specific_data.data.network_interfaces.manufacturer": "Manufacturer"
    }

    df.rename(columns=headers, inplace=True)

    final_name = f'{saved_query_name_clean}_{central}_{current_date_and_time}.xlsx'
    final_path = f'{base_path}/{final_name}'
    df.to_excel(final_path, index=False)

    # --------------------------------------------------
    # FORMATO OPENPYXL
    # --------------------------------------------------
    wb = openpyxl.load_workbook(final_path)
    ws = wb.active
    ws.title = saved_query_name_clean
    ws.auto_filter.ref = ws.dimensions

    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 30
        for cell in col:
            cell.alignment = Alignment(wrap_text=True)

    wb.save(final_path)
    wb.close()

    # --------------------------------------------------
    # DONE
    # --------------------------------------------------
    with open(f'{base_path}/done/{saved_query_name_clean}_{central}.done', "w") as f:
        f.write("done")

    mostrar_tabla(centrales, current_date_and_time)


# ======================================================
# MAIN
# ======================================================

def main():
    from centrales import centrales

    dotenv_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    connect_args = {
        "url": os.getenv("AXONIUS_URL"),
        "key": os.getenv("AXONIUS_KEY"),
        "secret": os.getenv("AXONIUS_SECRET"),
        "verify": False
    }

    for central in centrales:
        base = f'./ARCHIVOS_REPORTES/{central.nombre}/{current_date_and_time}'
        os.makedirs(f'{base}/done', exist_ok=True)

        for i in range(len(central.queries)):
            axonius_retreive_data(
                connect_args=connect_args,
                saved_query_name=central.queries[i],
                saved_query_name_clean=central.file_name[i],
                central=central.nombre,
                current_date_and_time=current_date_and_time
            )


if __name__ == "__main__":
    main()
