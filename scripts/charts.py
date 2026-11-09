import os
import datetime as dt
from openpyxl import load_workbook
import csv
import xlwings as xw
from centrales import centrales
from openpyxl.chart import LineChart, Reference
from openpyxl.utils import get_column_letter
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.colors import ColorChoice
from copy import copy
from openpyxl.styles import Alignment, Border, Side
import re
import json
from pathlib import Path

PATRON_CACR = re.compile(r"^CACR[1-9]$")

def es_cacr(central):
    return bool(PATRON_CACR.match(central))

def contar_tabletas(central):
    json_path = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON" / "ALL_GENERAL_TABLETS.json"
    if not json_path.exists():
        raise FileNotFoundError(json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        devices = json.load(f)

    if central == "GENERAL":
        # total, contando cada activo una sola vez (igual que count_assets_simple)
        return len({d.get("internal_axon_id") for d in devices if d.get("internal_axon_id")})

    return sum(1 for d in devices if central in d.get("labels", []))


def agregar_fila_tabletas_general():
    central = "GENERAL"
    fecha_hoy = dt.date.today().strftime("%Y-%m-%d")
    ruta_reporte = os.path.abspath(os.path.join(
        "ARCHIVOS_REPORTES", central, fecha_hoy,
        f"Reporte_Disc_Con_Sin_Clasificacion_{fecha_hoy}.xlsx"
    ))
    if not os.path.exists(ruta_reporte):
        print("No se encontró el reporte GENERAL.")
        return

    tabletas = contar_tabletas(central)

    # ---------- FASE 1: insertar fila con Excel (xlwings) ----------
    insertada = False
    wb = xw.Book(ruta_reporte)
    try:
        ws = wb.sheets["Resumen"]
        if ws.range("C15").value != "Tabletas":   # si ya existe, no insertar de nuevo
            ws.range("15:15").insert(shift="down", copy_origin="format_from_left_or_above")
            ws.range("C15").value = "Tabletas"
            ws.range("F15").value = tabletas
            ws.range("F4").formula = "=F5+F10+F13+F14+F15"
            wb.app.calculate()
            wb.save()
            insertada = True
    finally:
        wb.close()

    if not insertada:
        return

    # ---------- FASE 2: merges y formato con openpyxl ----------
    wb = load_workbook(ruta_reporte)
    ws = wb["Resumen"]

    # 1) Unmerge de lo que contenga A4 o B5 (y lo que haya heredado la fila 15)
    for rng in list(ws.merged_cells.ranges):
        if "A4" in rng or "B5" in rng or rng.min_row <= 15 <= rng.max_row and rng.min_col >= 3:
            ws.unmerge_cells(str(rng))

    # 2) Formato de C14:F14 -> C15:F15 (con bordes)
    for col in range(3, 7):
        origen = ws.cell(row=14, column=col)
        destino = ws.cell(row=15, column=col)
        destino.font = copy(origen.font)
        destino.border = copy(origen.border)
        destino.fill = copy(origen.fill)
        destino.number_format = origen.number_format
        destino.protection = copy(origen.protection)
        destino.alignment = copy(origen.alignment)

    # 3) Si la fila 14 tiene merge (p. ej. C14:E14), replicarlo en la 15
    for rng in list(ws.merged_cells.ranges):
        if rng.min_row == 14 and rng.max_row == 14 and rng.min_col >= 3:
            ws.merge_cells(start_row=15, start_column=rng.min_col,
                           end_row=15, end_column=rng.max_col)

    # 4) Merges nuevos
    ws.merge_cells("A4:A17")
    ws.merge_cells("B5:B15")

    wb.save(ruta_reporte)
    wb.close()


def sobrescribir_registro_csv(ruta_csv, fila_nueva):
    fecha_hoy = fila_nueva[0]
    registros = []
    encabezado = None

    if os.path.exists(ruta_csv):
        with open(ruta_csv, mode="r", newline="") as file:
            reader = csv.reader(file)
            registros = list(reader)

        if registros:
            encabezado = registros[0]
            datos = registros[1:]
        else:
            datos = []
    else:
        datos = []

    datos_filtrados = [fila for fila in datos if fila and fila[0] != fecha_hoy]
    datos_filtrados.append(fila_nueva)

    if not encabezado:
        encabezado = ["Date"] + [f"Value{i+1}" for i in range(len(fila_nueva)-1)]

    with open(ruta_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(encabezado)
        writer.writerows(datos_filtrados)

def data_central(central):
    ruta_base = "ARCHIVOS_REPORTES"
    current_date_and_time = str(dt.date.today())
    if central == "GENERAL":
        nombre_archivo = f"Reporte_Disc_Con_Sin_Clasificacion_{current_date_and_time}.xlsx"
    else:
        nombre_archivo = f"Reporte_Discovery_{central}_{current_date_and_time}.xlsx"
    ruta_completa = os.path.join(ruta_base, central, current_date_and_time, nombre_archivo)

    carpeta_script = os.path.dirname(os.path.realpath(__file__))
    ruta_graficas_dir = os.path.abspath(os.path.join(carpeta_script, "..", "src", "Graficas"))
    ruta_csv = os.path.join(ruta_graficas_dir, f"data_{central}.csv")

    if not os.path.exists(ruta_graficas_dir):
        os.makedirs(ruta_graficas_dir)

    wb = xw.Book(ruta_completa)

    # ---- NUEVO: solo CACR1..CACR9 ----
    if es_cacr(central):
        ws_res = wb.sheets["Resumen"]
        if ws_res.range("C15").value != "Tabletas":   # si ya tiene la fila, no tocar
            ws_res.range("G14").value = contar_tabletas(central)
            ws_res.range("F4").formula = "=F5+F10+F13+F14+G14"
    # ----------------------------------

    wb.app.calculate()
    wb.save()
    wb.close()

    if os.path.exists(ruta_completa):
        try:
            wb_origen = load_workbook(ruta_completa, data_only=True)
            if "Resumen" in wb_origen.sheetnames:
                hoja = wb_origen["Resumen"]

                # Si ya existe la fila Tabletas, lo de abajo se recorrió 1 fila
                off = 1 if hoja["C15"].value == "Tabletas" else 0

                assets = hoja["F3"].value
                identified_dev = hoja["F4"].value
                servers_t = hoja["F5"].value
                servers_c = hoja["F6"].value
                servers_noc = str(int(hoja["F7"].value))
                unidentified_serv = hoja[f"F{15 + off}"].value
                unmanagged = hoja[f"F{16 + off}"].value
                wb_origen.close()
            else:
                print("La hoja 'Resumen' no existe.")
                return None
        except Exception as e:
            print(f"Error al abrir el archivo origen: {e}")
            return None

        try:
            fecha_formateada = dt.date.today().strftime("%d/%m/%y")
            fila_nueva = [fecha_formateada, assets, identified_dev, servers_c, servers_noc, unidentified_serv, unmanagged, servers_t]
            sobrescribir_registro_csv(ruta_csv, fila_nueva)
        except Exception as e:
            print(ruta_completa)
            print(f"Error al escribir en el CSV: {e}")
    else:
        print(f"El archivo origen no existe: {ruta_completa}")
        return False
def agregar_fila_tabletas(central):
    if not es_cacr(central):
        return

    fecha_hoy = dt.date.today().strftime("%Y-%m-%d")
    ruta_reporte = os.path.join(
        "ARCHIVOS_REPORTES", central, fecha_hoy,
        f"Reporte_Discovery_{central}_{fecha_hoy}.xlsx"
    )
    if not os.path.exists(ruta_reporte):
        print(f"No se encontró el reporte de {central}.")
        return

    # ---------- FASE 1: insertar fila con Excel (xlwings) ----------
    wb = xw.Book(ruta_reporte)
    try:
        ws = wb.sheets["Resumen"]

        if ws.range("C15").value == "Tabletas":
            return  # ya fue insertada

        tabletas = ws.range("G14").value
        if tabletas is None:
            tabletas = contar_tabletas(central)

        # Inserta fila 15 copiando el formato de la fila 14
        ws.range("15:15").insert(shift="down", copy_origin="format_from_left_or_above")

        ws.range("C15").value = "Tabletas"
        ws.range("F15").value = tabletas
        ws.range("G14").clear_contents()
        ws.range("F4").formula = "=F5+F10+F13+F14+F15"

        wb.app.calculate()
        wb.save()
    finally:
        wb.close()

    # ---------- FASE 2: merges y bordes con openpyxl ----------
    wb = load_workbook(ruta_reporte)
    ws = wb["Resumen"]

    def unmerge_si_contiene(coords):
        for rng in list(ws.merged_cells.ranges):
            if any(c in rng for c in coords):
                ws.unmerge_cells(str(rng))

    def set_borde(cell, **lados):
        b = cell.border
        cell.border = Border(
            left=lados.get("left", b.left),
            right=lados.get("right", b.right),
            top=lados.get("top", b.top),
            bottom=lados.get("bottom", b.bottom),
        )

    linea = Side(style="thin")

    # 1) Unmerge de B5 y de lo que haya en C15:E15 (por si heredó merge de la fila 14)
    unmerge_si_contiene(["B5", "B15", "C15", "D15", "E15"])

    # 2) Merge B5:B15 (conserva el valor de B5)
    ws.merge_cells("B5:B15")

    # 3) Merge C15:E15, alineado a la izquierda, borde derecho
    ws.merge_cells("C15:E15")
    for col in ("C", "D", "E"):
        c = ws[f"{col}15"]
        c.alignment = Alignment(
            horizontal="left",
            vertical=c.alignment.vertical,
            wrap_text=c.alignment.wrap_text,
        )
        set_borde(c, right=linea)        # el borde derecho lo marca E15

    # 4) F15: borde izquierdo, derecho e inferior
    set_borde(ws["F15"], left=linea, right=linea, bottom=linea)

    wb.save(ruta_reporte)
    wb.close()

def agregar_hojas_graficas(central):
    fecha_hoy = dt.date.today().strftime("%Y-%m-%d")

    if central == "GENERAL":    
        ruta_reporte = os.path.join("ARCHIVOS_REPORTES", central, fecha_hoy, f"Reporte_Disc_Con_Sin_Clasificacion_{fecha_hoy}.xlsx")
    else:
        ruta_reporte = os.path.join("ARCHIVOS_REPORTES", central, fecha_hoy, f"Reporte_Discovery_{central}_{fecha_hoy}.xlsx")

    carpeta_script = os.path.dirname(os.path.realpath(__file__))
    ruta_csv = os.path.abspath(os.path.join(carpeta_script, "..", "src", "Graficas", f"data_{central}.csv"))

    if not os.path.exists(ruta_reporte):
        print(f"No se encontró el archivo de reporte para {central}.")
        return

    try:
        wb = load_workbook(ruta_reporte)

        def crear_hoja_con_grafica(wb, nombre_hoja, ruta_csv, columnas_numericas):
            if nombre_hoja in wb.sheetnames:
                del wb[nombre_hoja]
            ws = wb.create_sheet(nombre_hoja)

            with open(ruta_csv, newline='') as f:
                reader = csv.reader(f)
                for row_idx, row in enumerate(reader, start=1):
                    for col_idx, valor in enumerate(row, start=1):
                        if row_idx > 1 and col_idx in columnas_numericas:
                            try:
                                valor = float(valor.replace(",", "")) if isinstance(valor, str) else float(valor)
                            except:
                                pass
                        ws.cell(row=row_idx, column=col_idx).value = valor


            ws.sheet_view.zoomScale = 110
            ws.sheet_view.topLeftCell = "J2"

            chart = LineChart()
            if central == "GENERAL":
                chart.title ="Tendencia Con/Sin Clasificacion"
            else:
                chart.title = f"Resumen {central}"
            chart.style = 2
            chart.y_axis.title = "Cantidad"
            chart.x_axis.title = "Fecha"

            # Ampliar tamaño visual
            chart.width = 38
            chart.height = 20

            max_row = ws.max_row
            for col_idx in columnas_numericas:
                data = Reference(ws, min_col=col_idx, min_row=1, max_row=max_row)
                chart.add_data(data, titles_from_data=True)
            colors = ["FF0000", "0000FF", "00AA00", "FFA500", "800080", "008080", "808000"]  
            for serie, color in zip(chart.series, colors):
                serie.graphicalProperties.line.solidFill = color
                serie.graphicalProperties.line.width = 35000  

            cats = Reference(ws, min_col=1, min_row=2, max_row=max_row)
            chart.set_categories(cats)

            col_chart = get_column_letter(max(columnas_numericas) + 2)
            ws.add_chart(chart, f"{col_chart}2")

        crear_hoja_con_grafica(wb, f"Data_{central}", ruta_csv, [2,3,4,5,6,7,8])
        wb.save(ruta_reporte)
        wb.close()

    except Exception as e:
        print(f"Error al crear hojas con gráficas: {e}")

if __name__ == '__main__':
    for central in centrales:
        try:
            data_central(central.nombre)
            agregar_hojas_graficas(central.nombre)
            if central.nombre == "GENERAL":
                agregar_fila_tabletas_general()
            else:
                agregar_fila_tabletas(central.nombre)
        except Exception as e:
            print(f"Error : {e}")
    #data_central("IXTLA")
    #agregar_hojas_graficas("IXTLA")