import shutil
import os
import datetime as dt
import openpyxl
from copy import copy
from collections import Counter
from time import sleep
import openpyxl.styles
from openpyxl.utils import get_column_letter
#from new_queries import new_queries
from new_queries_NEW import new_queries, load_from_json
import time
import re
import shutil
from openpyxl.utils import quote_sheetname
import json
from pathlib import Path
from datetime import datetime

name = 'Reporte_Discovery'
origin_path = f'./src/{name}.xlsx'
#central = 'IXTLA'
current_date_and_time = str(dt.date.today())


# ======================================================
# CAC (centrales CACR1..CACR9): columna "CAC" al final de cada hoja
# ======================================================
CAC_CENTRAL_PATTERN = re.compile(r"CACR[1-9]")

# Tokens que NO son parte del nombre del sitio y se quitan si van al INICIO del
# label (CAC_CAC_..., MCI_CAC_..., CAC_CVT_...). Si aparece otro prefijo, agregalo aqui.
CAC_PREFIJOS = {"CAC", "MCI", "CVT"}
CAC_REGION_PATTERN = re.compile(r"R\d+")      # token final de region (R1, R9, ...) que tambien se quita

# hoja -> (ultima columna actual, filas de encabezado (arriba, abajo), fila del filtro)
CAC_HOJAS = {
    'Inventario - PC':             (7,  (4, 5), 5),    # G -> H
    'Inventario - Red':            (6,  (4, 4), 4),    # F -> G
    'Inventario':                  (10, (4, 5), 5),    # J -> K
    'Inventario - EOL':            (8,  (4, 5), 5),    # H -> I
    'Inventario No Identificados': (5,  (4, 4), 4),    # E -> F
    'Inventario Identificados':    (5,  (4, 4), 4),    # E -> F
}


def is_cac_central(central):
    return bool(CAC_CENTRAL_PATTERN.fullmatch(str(central).strip()))


def _cac_site(label):
    original = str(label).strip()
    tokens = [t for t in original.split("_") if t]
    while tokens and tokens[0].upper() in CAC_PREFIJOS:
        tokens.pop(0)
    if tokens and CAC_REGION_PATTERN.fullmatch(tokens[-1].upper()):
        tokens.pop()
    site = " ".join(tokens)
    return site if site else original


def _cac_es_label_cac(label):
    """True si el label hace referencia a un CAC (CAC, CVT, MCI...) en alguno de sus dos primeros tokens.
    Descarta basura como '1'. Los prefijos validos estan en CAC_PREFIJOS."""
    tokens = [t for t in str(label).strip().split("_") if t]
    return any(t.upper() in CAC_PREFIJOS for t in tokens[:2])


def cac_names(label):
    """Lista (sin repetidos) de sitios a partir de un label o una lista de labels.
    Solo toma los labels que hacen referencia a un CAC; el resto ('1', '1', etc.) se ignora."""
    if label is None:
        return []
    items = label if isinstance(label, (list, tuple, set)) else [label]
    names = []
    for item in items:
        if item is None:
            continue
        # el Excel intermedio guarda varios labels separados por salto de linea (tambien se acepta coma o ;)
        for part in re.split(r"[\n,;]+", str(item)):
            part = part.strip()
            if not part or not _cac_es_label_cac(part):
                continue
            name = _cac_site(part)
            if name not in names:
                names.append(name)
    return names


def cac_from_label(label):
    """CAC_CAC_HUEHUETOCA_R9 -> HUEHUETOCA ; CAC_CVT_MULTIPLAZA_LINDAVISTA_R4 -> MULTIPLAZA LINDAVISTA"""
    return ", ".join(cac_names(label))


def find_label_col(ws, header_row=1, fallback=None):
    """Columna cuyo encabezado contiene 'connection' en un Excel intermedio."""
    for cell in ws[header_row]:
        if cell.value is not None and "connection" in str(cell.value).lower():
            return cell.column
    return fallback


def copy_cell_style(src, tgt):
    tgt.font = copy(src.font)
    tgt.border = copy(src.border)
    tgt.fill = copy(src.fill)
    tgt.number_format = copy(src.number_format)
    tgt.protection = copy(src.protection)
    tgt.alignment = copy(src.alignment)


def agregar_columna_cac(ws, hoja, last_data_row, values_by_row, width=35):
    """
    Agrega la columna CAC a la derecha de la ultima columna de `hoja`:
      1) desombina A3 y vuelve a combinar el titulo A3:<columna nueva>3
      2) copia el formato de <ultima columna>4..<ultima columna>[ultima fila] a la columna nueva
      3) escribe el encabezado 'CAC' (y combina filas 4-5 si el encabezado es de 2 filas)
      4) escribe los valores {fila: valor}
      5) pone el autofiltro hasta la columna nueva
    """
    last_col, (top, bottom), filter_row = CAC_HOJAS[hoja]
    new_col = last_col + 1
    new_letter = get_column_letter(new_col)
    last_data_row = max(last_data_row, bottom)

    # 1) titulo A3: unmerge y merge de nuevo hasta la columna nueva
    for rng in list(ws.merged_cells.ranges):
        if rng.min_row <= 3 <= rng.max_row and rng.min_col <= 1 <= rng.max_col:
            ws.unmerge_cells(str(rng))
    for c in range(2, new_col + 1):
        copy_cell_style(ws.cell(row=3, column=1), ws.cell(row=3, column=c))
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=new_col)

    # 2) formato de la ultima columna -> columna nueva
    for r in range(top, last_data_row + 1):
        copy_cell_style(ws.cell(row=r, column=last_col), ws.cell(row=r, column=new_col))

    # 3) encabezado
    ws.cell(row=top, column=new_col).value = "CAC"
    if bottom > top:
        ws.merge_cells(start_row=top, start_column=new_col, end_row=bottom, end_column=new_col)

    # 4) valores (labels)
    for r, v in values_by_row.items():
        ws.cell(row=r, column=new_col).value = v

    # 5) filtro y ancho
    ws.auto_filter.ref = f"A{filter_row}:{new_letter}{filter_row}"
    ws.column_dimensions[new_letter].width = width
    return new_col


def cac_hojas_identificados(central, path_rep):
    """CAC en 'Inventario No Identificados' e 'Inventario Identificados' (despues de new_queries)."""
    if not is_cac_central(central):
        return
    hojas = {
        "Inventario No Identificados": "ALL_GENERAL_UNIDENTIFIED_SERVERS.json",
        "Inventario Identificados": "GENERAL_VARIOUS_IDENTIFIED_DEVICES.json",
    }
    wb = openpyxl.load_workbook(path_rep)
    for hoja, json_name in hojas.items():
        # mismo JSON, mismo filtro y mismo orden que usa new_queries -> fila 5 + i
        devices = load_from_json(json_name, central)
        values = {5 + i: cac_from_label(d.get("specific_data.connection_label"))
                  for i, d in enumerate(devices)}
        agregar_columna_cac(wb[hoja], hoja, 4 + len(devices), values)
    wb.save(path_rep)
    wb.close()

def copy_style_from_row(ws, source_row, start_row, end_row):
    for row in range(start_row, end_row + 1):
        for col in range(1, ws.max_column + 1):
            source_cell = ws.cell(row=source_row, column=col)
            target_cell = ws.cell(row=row, column=col)

            # Copiar estilos individuales
            target_cell.font = copy(source_cell.font)
            target_cell.border = copy(source_cell.border)
            target_cell.fill = copy(source_cell.fill)
            target_cell.number_format = copy(source_cell.number_format)
            target_cell.protection = copy(source_cell.protection)
            target_cell.alignment = copy(source_cell.alignment)


def get_strictly_unique_combinations(central):
    path = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path = path + r'/' + f'EOL_{central}_{current_date_and_time}.xlsx'
    wb = openpyxl.load_workbook(des_path, data_only=True)
    ws = wb.active

    combos = []

    # Iterate over rows and extract values from B, G, H, I (columns 2, 7, 8, 9)
    for row in ws.iter_rows(min_row=2, max_col=11):  # Read up to column I
        b = row[1].value  # Column B (index 1)
        g = row[6].value  # Column G (index 6)
        h = row[7].value  # Column H (index 7)
        i = row[8].value  # Column I (index 8)
        j = row[9].value  # Column I (index 9)
        k = row[10].value  # Column I (index 10)
        combo = (b, g, h, i,j,k)
        combos.append(combo)

    # Contar cuántas veces aparece cada combinación
    counter = Counter(combos)

    return counter


def get_cac_por_combo(central):
    """
    CAC: para cada combinacion del EOL (misma llave que get_strictly_unique_combinations)
    junta los sitios (CAC) donde aparece, separados por coma.
    Retorna {combo: "SITIO1, SITIO2"} o None si el EOL_ no trae columna Connection Label.
    """
    path = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path = path + r'/' + f'EOL_{central}_{current_date_and_time}.xlsx'
    wb = openpyxl.load_workbook(des_path, data_only=True)
    ws = wb.active

    label_col = find_label_col(ws)
    if label_col is None:
        wb.close()
        return None

    sitios = {}
    for row in ws.iter_rows(min_row=2, max_col=max(11, label_col)):
        combo = (row[1].value, row[6].value, row[7].value, row[8].value, row[9].value, row[10].value)
        lista = sitios.setdefault(combo, [])
        for site in cac_names(row[label_col - 1].value):
            if site not in lista:
                lista.append(site)
    wb.close()
    return {combo: ", ".join(lista) for combo, lista in sitios.items()}


def eol(central):
    #counter, strictly_unique_combos = get_strictly_unique_combinations(central=central)
    counter = get_strictly_unique_combinations(central=central)
    path_rep = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path_rep = path_rep + r'/' + f'Reporte_Discovery_{central}_{current_date_and_time}.xlsx'
    wb_rep = openpyxl.load_workbook(des_path_rep)
    ws_rep = wb_rep[f'Inventario - EOL']
    aux = 1
    for combo, count in counter.items():
        ws_rep[f'A{aux+5}'].value = aux
        ws_rep[f'B{aux+5}'].value = combo[0]
        ws_rep[f'C{aux+5}'].value = combo[1]
        ws_rep[f'D{aux+5}'].value = combo[2]
        ws_rep[f'E{aux+5}'].value = combo[3]
        ws_rep[f'F{aux+5}'].value = combo[4]
        ws_rep[f'G{aux+5}'].value = combo[5]
        ws_rep[f'H{aux+5}'].value = count
        aux += 1
    copy_style_from_row(ws=ws_rep,source_row=6,start_row=7,end_row=len(counter)+5)

    # CAC: columna I con los sitios donde aparece cada combinacion (separados por coma)
    if is_cac_central(central):
        sitios = get_cac_por_combo(central)
        if sitios is None:
            print(f"[CAC][AVISO] {central}: EOL_{central}_{current_date_and_time}.xlsx no tiene columna "
                  f"'Connection Label'; la columna CAC de 'Inventario - EOL' queda vacia.")
            sitios = {}
        values = {i + 6: sitios.get(combo, "") for i, combo in enumerate(counter.keys())}
        agregar_columna_cac(ws_rep, 'Inventario - EOL', len(counter) + 5, values)

    temp_path = des_path_rep.replace(".xlsx", "_temp.xlsx")
    wb_rep.save(temp_path)
    wb_rep.close()
    if os.path.exists(des_path_rep):
        os.remove(des_path_rep)  # Borrar el original (si existe)
    shutil.move(temp_path, des_path_rep)  # Renombrar el temporal al original
    return len(counter)



def totalAssets(central,file,serv):
    path = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path = path + r'/' + f'{file}_{central}_{current_date_and_time}.xlsx'
    wb = openpyxl.load_workbook(des_path, data_only=True)
    ws = wb.active
    aux = 0
    cortex = 0
    vp = 0
    if serv:
        for row in range(1, ws.max_row + 1):
            valor_f = ws[f'F{row}'].value
            valor_g = ws[f'G{row}'].value

            if valor_f == "SI":
                cortex += 1
            elif valor_f == "NO" and valor_g == "SI":
                vp += 1
        
    for cell in ws['A']:
        if cell.value not in (None,""):
            aux += 1
    wb.close()
    if aux == 0:    return 0,cortex,vp
    else:   return aux-1,cortex,vp

def getFormat(ws_rep, col, row,beg):
        prev_cell = ws_rep[f'{col}{row+beg}'] 
        new_cell = ws_rep[f'{col}{row+beg+1}']

        new_cell.font = copy(prev_cell.font)
        new_cell.fill = copy(prev_cell.fill)
        new_cell.border = copy(prev_cell.border)
        new_cell.alignment = copy(prev_cell.alignment)
        new_cell.number_format = copy(prev_cell.number_format)

def pcs_Inv(central,file, sheet):   
    unsupported_oses = [
    "Oracle Solaris", "Windows Server 2008 R2",
    "Windows Server 2003 R2", "SunOS 10", "SunOS 11.1",
    "SunOS 11.2", "SunOS 11.3", "IBM AIX 6.1", "IBM AIX 7.1",
    "IBM AIX 7.2", "IBM AIX 5.3", "SunOS 9", "SunOS 11.4.23.69.3",
    "SunOS 11.0", "SunOS 11.4", "SunOS 11.4.0.15.0",
    "Linux Red Hat 5", "Linux Red Hat 6",
    "IBM AIX 6","IBM AIX 0", "F5 Networks Big-IP",
    "HP HP-UX",
    "Cisco ISE", "Cisco IOS",
    "VMWare ESXi 6", "VMWare ESXi 6.5", "VMWare ESXi 7.0.3", "VMWare ESXi 8.0.3",
    "Linux FreeBSD", "Linux FreeBSD 6.2", "Linux FreeBSD 7.1", "Linux FreeBSD 8.2", "Linux FreeBSD 9.2", "Linux FreeBSD 11", "Linux FreeBSD 12",
    "Linux Photon OS (64-bit)",
    "Linux Arch 7",
    "Windows Server 2008", "Windows Server 2003", "Windows Server 2000",
    "Linux Fedora", "Linux Fedora 24",
    "Linux openSUSE 12.5", "Linux openSUSE 8.10"
    ]


    path_rep = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path_rep = path_rep + r'/' + f'Reporte_Discovery_{central}_{current_date_and_time}.xlsx'
    wb_rep = openpyxl.load_workbook(des_path_rep)
    ws_rep = wb_rep[f'{sheet}']
    
    path = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path = path + r'/' + f'{file}_{central}_{current_date_and_time}.xlsx'
    wb = openpyxl.load_workbook(des_path, data_only=True)
    ws = wb.active
    aux = False
    for row in range(2, ws.max_row + 1):
        if aux:
            for col in ['A', 'B', 'C', 'D', 'E', 'F','G', 'H', 'I', 'J']:
                getFormat(ws_rep, col, row,beg=3)
        ws_rep[f'A{row+4}'].value = row-1
        ws_rep[f'B{row+4}'].value = ws[f'B{row}'].value
        ws_rep[f'C{row+4}'].value = ws[f'C{row}'].value
        ws_rep[f'D{row+4}'].value = ws[f'D{row}'].value
        ws_rep[f'E{row+4}'].value = ws[f'E{row}'].value
        ws_rep[f'F{row+4}'].value = ws[f'F{row}'].value

        # =====================================================
        # PCs
        # SOLO PARA IXTLA:
        # mover COMMENTS a columna H
        # =====================================================

        ws_rep[f'G{row+4}'].value = ws[f'G{row}'].value

        if file == 'PCs' and central == "IXTLA":

            # Vaciar columna G
            ws_rep[f'G{row+4}'].value = ""

            # Copiar SIEMPRE formato G -> H
            source_cell = ws_rep[f'G{row+4}']
            target_cell = ws_rep[f'H{row+4}']

            target_cell.font = copy(source_cell.font)
            target_cell.fill = copy(source_cell.fill)
            target_cell.border = copy(source_cell.border)
            target_cell.alignment = copy(source_cell.alignment)
            target_cell.number_format = copy(source_cell.number_format)

            # Width columna H
            ws_rep.column_dimensions['H'].width = 20
            # Copiar comentario
            comment = ws[f'I{row}'].value

            if comment not in (None, ""):
                ws_rep[f'H{row+4}'].value = comment

        conditions = ', '.join([f'E{row+4}="{os}"' for os in unsupported_oses])
        #formula = f'=IF(OR({conditions}), "Cortex not supported", "NA")'
        formula = (
            f'=IF(F{row+4}="SI", "NA", '
            f'IF(OR({conditions}), "Cortex not supported", "NA"))'
        )
        if file == 'SERVERS':

            # SOLO IXTLA
            if central == "IXTLA":

                comment = ws[f'I{row}'].value

                if comment not in (None, ""):

                    # Obtener resultado esperado de la fórmula
                    if ws[f'F{row}'].value == "SI":
                        formula_result = "NA"

                    elif ws[f'E{row}'].value in unsupported_oses:
                        formula_result = "Cortex not supported"

                    else:
                        formula_result = "NA"

                    # Si el resultado es NA, no agregarlo
                    if formula_result == "NA":
                        ws_rep[f'J{row+4}'].value = "DISCOVERED VIA NMAP"
                    else:
                        ws_rep[f'J{row+4}'].value = (
                            f'DISCOVERED VIA NMAP | {formula_result}'
                        )

                else:
                    ws_rep[f'J{row+4}'].value = formula

            # RESTO DE CENTRALES
            else:
                ws_rep[f'J{row+4}'].value = formula

        aux = True

    # CAC: columna H (Inventario - PC) / K (Inventario) desde Connection Label del Excel intermedio
    if is_cac_central(central):
        label_col = find_label_col(ws)
        if label_col is None:
            print(f"[CAC][AVISO] {central}: {file}_{central}_{current_date_and_time}.xlsx no tiene columna "
                  f"'Connection Label'; la columna CAC de '{sheet}' queda vacia.")
            values = {}
        else:
            values = {r + 4: cac_from_label(ws.cell(row=r, column=label_col).value)
                      for r in range(2, ws.max_row + 1)}
        agregar_columna_cac(ws_rep, sheet, ws.max_row + 4, values)

    temp_path = des_path_rep.replace(".xlsx", "_temp.xlsx")
    wb_rep.save(temp_path)
    wb_rep.close()
    wb.close()
    if os.path.exists(des_path_rep):
        os.remove(des_path_rep)  # Borrar el original (si existe)
    shutil.move(temp_path, des_path_rep)  # Renombrar el temporal al original


def get_strictly_unique_combinations_vuln(central,vuln):
    path = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path = path + r'/' + f'{vuln}_SEV_{central}_{current_date_and_time}.xlsx'
    wb = openpyxl.load_workbook(des_path, data_only=True)
    ws = wb[f'{vuln}_SEV_{central}_{current_date_and_time}']

    combos = []

    # Iterate over rows and extract values from B, G, H, I (columns 2, 7, 8, 9)
    for row in ws.iter_rows(min_row=2, max_col=7):  # Read up to column I
        b = row[5].value  # Column B (index 1)
        combo = (b)
        combos.append(combo)

    # Contar cuántas veces aparece cada combinación
    counter = Counter(combos)
    return counter

def vuln(vulnerabilitie,central,path_rep):
    path_rep = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path = path_rep + r'/' + f'{vulnerabilitie}_SEV_{central}_{current_date_and_time}.xlsx'
    if not os.path.exists(des_path):
        path_rep = path_rep + r'/' + f'Reporte_Discovery_{central}_{current_date_and_time}.xlsx'
        wb = openpyxl.load_workbook(path_rep)
        ws = wb[f'Inventario']
        for row in range(6, ws.max_row+1):
            ws[f'H{row}'].value = 0
            ws[f'I{row}'].value = 0
        if vulnerabilitie == 'CRITICAL':
            sheet_reporte = wb[f'Resumen']
            sheet_reporte['E20'].value = 0
        elif vulnerabilitie == 'HIGH':
            sheet_reporte = wb[f'Resumen']
            sheet_reporte['E21'].value = 0

        wb.save(path_rep)
        wb.close()
        return
    path_reporte = path_rep + r'/' + f'Reporte_Discovery_{central}_{current_date_and_time}.xlsx'
    file_reporte = openpyxl.load_workbook(path_reporte)
    sheet_reporte = file_reporte[f'Inventario']

    counter = get_strictly_unique_combinations_vuln(central=central, vuln=vulnerabilitie)
    
    for row_rep in range(6, sheet_reporte.max_row+1):
        aux = False
        for combo, count in counter.items():
            if sheet_reporte[f'B{row_rep}'].value == combo:
                if vulnerabilitie == 'CRITICAL':
                    sheet_reporte[f'H{row_rep}'].value = count
                    aux = True
                elif vulnerabilitie == 'HIGH':
                    sheet_reporte[f'I{row_rep}'].value = count
                    aux = True
        if not aux:
            if vulnerabilitie == 'CRITICAL':
                sheet_reporte[f'H{row_rep}'].value = 0
            elif vulnerabilitie == 'HIGH':
                sheet_reporte[f'I{row_rep}'].value = 0

    
    file_reporte.save(path_reporte)
    file_reporte.close()

def esperar_archivos(central, fecha, carpeta_base="./ARCHIVOS_REPORTES"):
    flag_path = [
        f'./ARCHIVOS_REPORTES/{central}/{fecha}/done/critical_{central}.done',
        f'./ARCHIVOS_REPORTES/{central}/{fecha}/done/high_{central}.done',
        f'./ARCHIVOS_REPORTES/{central}/{fecha}/done/eol_{central}.done',
        f'./ARCHIVOS_REPORTES/{central}/{fecha}/done/NET_DEV_{central}.done',
        f'./ARCHIVOS_REPORTES/{central}/{fecha}/done/SERVERS_{central}.done',
        f'./ARCHIVOS_REPORTES/{central}/{fecha}/done/TOTAL_ASSETS_{central}.done',
        f'./ARCHIVOS_REPORTES/{central}/{fecha}/done/PCs_{central}.done',
    ]
    while True:
        if all(os.path.exists(path) for path in flag_path):
            break
        time.sleep(1)  # Esperar 1 segundo antes de volver a revisar

def verificar_archivo(central):
    # Ruta de la carpeta donde debe estar
    ruta_base = "ARCHIVOS_REPORTES"
    ruta_completa = os.path.join(ruta_base, central, current_date_and_time)

    # Verificar si la carpeta central existe
    if not os.path.isdir(ruta_completa):
        return False  # La carpeta no existe
    
    nombre_archivo = f"EOL_{central}_{current_date_and_time}.xlsx"

    # Verificar si el archivo "vuln.csv" está dentro de central
    return nombre_archivo in os.listdir(ruta_completa)

def count_assets(central):
    json_path = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON" / "GENERAL_ASSETS.json"

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    count = sum (1 for asset in data if "labels" in asset and central in asset["labels"])

    return count

def Report(central2):
    central = central2.nombre
    full_Name = central2.fullName
    from table import mostrar_tabla
    from centrales  import centrales
    mostrar_tabla(centrales, current_date_and_time)
    esperar_archivos(
        central=central,
        fecha=current_date_and_time,
    )
    path = r'./ARCHIVOS_REPORTES/'+central
    if not os.path.exists(path):
        os.mkdir(path)
    path = path + r'/'+current_date_and_time
    if not os.path.exists(path):
        os.mkdir(path)
    des_path = path + r'/' + f'{name}_{central}_{current_date_and_time}.xlsx'
    shutil.copy(origin_path, des_path)

    wb = openpyxl.load_workbook(des_path)
    ws = wb['Inventario - Red']
    path_aux = path + r'/' + f'NET_DEV_{central}_{current_date_and_time}.xlsx'
    wb_aux = openpyxl.load_workbook(path_aux)
    ws_aux = wb_aux.active

    # Limpia de la fila 2 hacia abajo
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row):
        for cell in row:
            cell.value = None
    # CAC: columna Connection Label del NET_DEV (no se pega tal cual; se usa para la columna CAC)
    cac_label_col = find_label_col(ws_aux) if is_cac_central(central) else None
    # Recorrer filas y columnas
    for row in ws_aux.iter_rows(min_row=1):
        for cell in row:

            target_row = cell.row + 3

            # ============================================
            # SOLO IXTLA:
            # mover COMMENTS a columna G
            # ============================================

            if central == "IXTLA":

                # Saltar Connection Label original
                if cell.column == 7:
                    continue

                # COMMENTS -> columna G
                if cell.column == 8:

                    target_cell = ws.cell(row=target_row, column=7, value=cell.value)

                    # Copiar formato F -> G
                    source_cell = ws.cell(row=target_row, column=6)

                    target_cell.font = copy(source_cell.font)
                    target_cell.fill = copy(source_cell.fill)
                    target_cell.border = copy(source_cell.border)
                    target_cell.alignment = copy(source_cell.alignment)
                    target_cell.number_format = copy(source_cell.number_format)

                else:
                    ws.cell(row=target_row, column=cell.column, value=cell.value)

            else:
                if cac_label_col is not None and cell.column == cac_label_col:
                    continue
                ws.cell(row=target_row, column=cell.column, value=cell.value)

    # Determinar la última fila pegada
    last_row_written = ws_aux.max_row + 3  # porque comenzamos desde fila 1 y pegamos desde fila 2

    # Aplicar estilo de la fila 3 a todas las filas copiadas
    copy_style_from_row(ws, source_row=5, start_row=4, end_row=last_row_written)
    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
        ws[f"{col}4"].font = openpyxl.styles.Font(bold=True)
    # SOLO IXTLA incluye columna G en filtro
    if central == "IXTLA":
        fil = "A4:G4"
    else:
        fil = "A4:F4"

    ws.auto_filter.ref = fil
    
    ws['A3'].value = f"Network Devices {full_Name} - Inventario "
    if central == "IXTLA":
        # Deshacer merge anterior A3:F3
        try:
            ws.unmerge_cells('A3:F3')
        except:
            pass

        # Nuevo merge A3:G3
        ws.merge_cells('A3:G3')
    else:
        # Limpiar columna G completa
        for row in range(4, ws.max_row + 1):
            ws[f'G{row}'].value = None



    # Ajustar anchos de columna (opcional)
    for col in ws_aux.columns:
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = ws_aux.column_dimensions[col_letter].width

    # CAC: columna G en 'Inventario - Red' (la G original de Connection Label se limpia arriba)
    if is_cac_central(central):
        if cac_label_col is None:
            print(f"[CAC][AVISO] {central}: NET_DEV_{central}_{current_date_and_time}.xlsx no tiene columna "
                  f"'Connection Label'; la columna CAC de 'Inventario - Red' queda vacia.")
            values = {}
        else:
            values = {r + 3: cac_from_label(ws_aux.cell(row=r, column=cac_label_col).value)
                      for r in range(2, ws_aux.max_row + 1)}
        agregar_columna_cac(ws, 'Inventario - Red', last_row_written, values)

    wb.save(des_path)

    ws = wb[f'Resumen']
    ws['A2'].value = f'Inventario {full_Name} - Resumen'
    ws.column_dimensions['E'].width = 20
    ws = wb[f'Inventario - PC']

    # SOLO IXTLA
    # Expandir merge A3:G3 -> A3:H3
    if central == "IXTLA":

        try:
            ws.unmerge_cells('A3:G3')
        except:
            pass

        ws.merge_cells('A3:H3')

    ws['A3'].value = f'PCs {full_Name} - Inventario'

    if central == "IXTLA":

        # Merge H4:H5
        ws.merge_cells('H4:H5')

        # Título
        ws['H4'] = 'COMMENTS'

        # Copiar formato desde G4
        source_cell = ws['G4']
        target_cell = ws['H4']

        target_cell.font = copy(source_cell.font)
        target_cell.fill = copy(source_cell.fill)
        target_cell.border = copy(source_cell.border)
        target_cell.alignment = copy(source_cell.alignment)
        target_cell.number_format = copy(source_cell.number_format)

        # Width columna H
        ws.column_dimensions['H'].width = 20

        # Agregar filtro incluyendo H
        ws.auto_filter.ref = "A5:H5"
    ws = wb[f'Inventario']
    ws['A3'].value = f'Servidores {full_Name} - Inventario'
    ws = wb[f'Inventario - EOL']
    ws['A3'].value = f'Servidores EOL {full_Name} - Inventario'


    t_assets,cortex,vp = totalAssets(central=central,file='TOTAL_ASSETS',serv=False)
    ws = wb[f'Resumen']
    if central=="IXTLA":
        ws['F3'].value = t_assets
    else:
        ws['F3'].value = count_assets(central)
    t_serv,cortex,vp = totalAssets(central=central,file='SERVERS', serv=True)
    ws['F5'].value = t_serv
    ws['F6'].value = cortex
    #ws['F7'].value = vp #VIRTUAL PATCHING
    #ws['F8'].value = t_serv - cortex - vp #NO PROTEGIDOS
    ws['F7'].value = t_serv - cortex
    t_pcs,cortex,vp = totalAssets(central=central,file='PCs', serv=True)
    ws['F10'].value = t_pcs
    ws['F11'].value = cortex
    ws['F12'].value = t_pcs - cortex
    t_net,cortex,vp = totalAssets(central=central,file='NET_DEV', serv=False)
    ws['F13'].value = t_net
    wb.save(des_path)
    wb.close()
    pcs_Inv(central=central,file='PCs',sheet='Inventario - PC')
    pcs_Inv(central=central,file='SERVERS',sheet='Inventario')

    if not verificar_archivo(central=central):
        wb = openpyxl.load_workbook(des_path)
        ws = wb[f'Resumen']
        ws['E22'].value = 0
        ws = wb[f'Inventario - EOL']
        ws['A6'].value = ''
        ws['B6'].value = ''
        ws['C6'].value = ''
        ws['D6'].value = ''
        ws['E6'].value = ''
        ws['F6'].value = ''
        ws['G6'].value = ''
        ws['H6'].value = ''
        wb.save(des_path)
        wb.close()
    else:
        eol_total = eol(central=central)

        wb = openpyxl.load_workbook(des_path)
        ws = wb[f'Resumen']
        ws['E22'].value = eol_total
        wb.save(des_path)
        
        wb.close()



    vuln(vulnerabilitie = 'CRITICAL', central = central, path_rep = des_path)
    vuln(vulnerabilitie = 'HIGH', central = central, path_rep = des_path)
    path_rep = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    path_rep = path_rep + r'/' + f'Reporte_Discovery_{central}_{current_date_and_time}.xlsx'
    wb = openpyxl.load_workbook(path_rep)
    sheet_reporte = wb[f'Resumen']

    sheet_reporte['A19'].value = f'Servidores {full_Name} - Vulnerabilidades'

    if central != 'IXTLA':
        sheet_reporte['E20'].value = f"=COUNTIF('Inventario'!H6:H1048576,\">0\")"
        sheet_reporte['E21'].value = f"=COUNTIF('Inventario'!I6:I1048576,\">0\")"
    
    wb.save(path_rep)
    wb.close()##################################################################################################################
    new_queries(central,full_Name)
    cac_hojas_identificados(central, path_rep)   # CAC: No Identificados / Identificados
    done_path = f'./ARCHIVOS_REPORTES/{central}/{current_date_and_time}/done/Reporte_{central}.done'
    with open(done_path, 'w') as f:
        f.write("done")

    if central == 'IXTLA':
        wb = openpyxl.load_workbook(path_rep)
        ws = wb[f'Resumen']
        done_base_path = f'./ARCHIVOS_REPORTES/{central}/{current_date_and_time}/done'
        critical_done = f'{done_base_path}/critical_{central}.done'
        if os.path.exists(critical_done):
            with open(critical_done, "r") as f:
                lines = f.readlines()
                #print(f'ARCHIVO CRITICAL TIENE {lines} lineas')
                total_critical = int(lines[0].strip())
                ws["E20"] = total_critical
                #if len(lines) > 1:
                #    total_critical = int(lines[1].strip())
                #    ws["E20"] = total_critical
                #    print(f"EN IXTLA HAY {total_critical} de vulnerabilidades criticas")
        high_done = f'{done_base_path}/high_{central}.done'
        if os.path.exists(high_done):
            with open(high_done, "r") as f:
                lines = f.readlines()
                #print(f'ARCHIVO HIGH TIENE {lines} lineas')
                total_high = int(lines[0].strip())
                ws["E21"] = total_high
                #if len(lines) > 1:
                #    total_high = int(lines[1].strip())
                #    ws["E21"] = total_high
                #    print(f"EN IXTLA HAY {total_high} de vulnerabilidades altas")

        wb.save(path_rep)

        
    else:
        try:
            wb = openpyxl.load_workbook(path_rep)
            del wb['Adaptadores integrados']
            wb.save(path_rep)
            wb.close()
        except:
            pass
    from table import mostrar_tabla
    from centrales  import centrales
    mostrar_tabla(centrales, current_date_and_time)

def copy_Report(central):
    meses = {
    "01": "Enero",
    "02": "Febrero",
    "03": "Marzo",
    "04": "Abril",
    "05": "Mayo",
    "06": "Junio",
    "07": "Julio",
    "08": "Agosto",
    "09": "Septiembre",
    "10": "Octubre",
    "11": "Noviembre",
    "12": "Diciembre"
    }
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    now = datetime.now()
    year = now.strftime("%Y")
    month_number = now.strftime("%m")
    month_name = meses[month_number]
    path_rep = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    dest_dir = os.path.join(base_dir, "REPORTES_SEMANALES", year, month_name, current_date_and_time  )

    if central == "GENERAL":
        path_rep = path_rep + r'/' + f'Reporte_Disc_Con_Sin_Clasificacion_{current_date_and_time}.xlsx'
    else:
        path_rep = path_rep + r'/' + f'Reporte_Discovery_{central}_{current_date_and_time}.xlsx'


    os.makedirs(dest_dir, exist_ok=True)
    file_name = os.path.basename(path_rep)
    dest_path = os.path.join(dest_dir, file_name)
    shutil.copy2(path_rep, dest_path)