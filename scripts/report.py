import shutil
import os
import datetime as dt
import openpyxl
from copy import copy
from collections import Counter
from time import sleep
import openpyxl.styles
from openpyxl.utils import get_column_letter


name = 'Reporte_Discovery'
origin_path = f'./src/{name}.xlsx'
#central = 'IXTLA'
current_date_and_time = str(dt.date.today())

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


def eol(central):
    #counter, strictly_unique_combos = get_strictly_unique_combinations(central=central)
    counter = get_strictly_unique_combinations(central=central)
    path_rep = r'./ARCHIVOS_REPORTES/'+central+ r'/'+current_date_and_time
    des_path_rep = path_rep + r'/' + f'Reporte_Discovery_{central}_{current_date_and_time}.xlsx'
    wb_rep = openpyxl.load_workbook(des_path_rep)
    ws_rep = wb_rep[f'Inventario - EOL']
    aux = 1
    for combo, count in counter.items():
        ws_rep[f'A{aux+3}'].value = aux
        ws_rep[f'B{aux+3}'].value = combo[0]
        ws_rep[f'C{aux+3}'].value = combo[1]
        ws_rep[f'D{aux+3}'].value = combo[2]
        ws_rep[f'E{aux+3}'].value = combo[3]
        ws_rep[f'F{aux+3}'].value = combo[4]
        ws_rep[f'G{aux+3}'].value = combo[5]
        ws_rep[f'H{aux+3}'].value = count
        aux += 1

    for row in range(2, len(counter) + 1):
        for col in ['A', 'B', 'C', 'D', 'E', 'F','G', 'H']:
            getFormat(ws_rep, col, row , beg=2)

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
    return aux-1,cortex,vp

def getFormat(ws_rep, col, row,beg):
        prev_cell = ws_rep[f'{col}{row+beg}']  # Ej: B7 cuando row=2
        new_cell = ws_rep[f'{col}{row+beg+1}']   # Ej: B8 cuando row=2

        new_cell.font = copy(prev_cell.font)
        new_cell.fill = copy(prev_cell.fill)
        new_cell.border = copy(prev_cell.border)
        new_cell.alignment = copy(prev_cell.alignment)
        new_cell.number_format = copy(prev_cell.number_format)

def pcs_Inv(central,file, sheet):    
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
        ws_rep[f'G{row+4}'].value = ws[f'G{row}'].value
        if file == 'SERVERS':
            ws_rep[f'J{row+4}'].value = 'NA'

        aux = True
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
            sheet_reporte['E19'].value = 0
        elif vulnerabilitie == 'HIGH':
            sheet_reporte = wb[f'Resumen']
            sheet_reporte['E20'].value = 0

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




def Report(central):
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
    for row in ws.iter_rows(min_row=3, max_row=ws.max_row):
        for cell in row:
            cell.value = None
    # Recorrer filas y columnas
    for row in ws_aux.iter_rows(min_row=1):
        for cell in row:
            # Ajustar fila de destino para que empiece también desde la fila 2
            target_row = cell.row + 1 # ya empieza desde 2, no hay que ajustar nada más
            ws.cell(row=target_row, column=cell.column, value=cell.value)

    # Determinar la última fila pegada
    last_row_written = ws_aux.max_row + 1  # porque comenzamos desde fila 1 y pegamos desde fila 2

    # Aplicar estilo de la fila 3 a todas las filas copiadas
    copy_style_from_row(ws, source_row=3, start_row=2, end_row=last_row_written)
    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
        ws[f"{col}2"].font = openpyxl.styles.Font(bold=True)
    fil = "A2:F2"
    ws.auto_filter.ref = fil
    ws['A1'].value = f"Network Devices {central} - Inventario "

    # Ajustar anchos de columna (opcional)
    for col in ws_aux.columns:
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = ws_aux.column_dimensions[col_letter].width
    wb.save(des_path)

    ws = wb[f'Resumen']
    ws['A2'].value = f'Inventario {central} - Resumen'
    ws = wb[f'Inventario - PC']
    ws['A3'].value = f'PCs {central} - Inventario'
    ws = wb[f'Inventario']
    ws['A3'].value = f'Servidores {central} - Inventario'
    ws = wb[f'Inventario - EOL']
    ws['A1'].value = f'Servidores EOL {central} - Inventario'

    t_assets,cortex,vp = totalAssets(central=central,file='TOTAL_ASSETS',serv=False)
    ws = wb[f'Resumen']
    ws['E3'].value = t_assets
    t_serv,cortex,vp = totalAssets(central=central,file='SERVERS', serv=True)
    ws['E5'].value = t_serv
    ws['E6'].value = cortex
    ws['E7'].value = vp
    ws['E8'].value = t_serv - cortex - vp
    t_pcs,cortex,vp = totalAssets(central=central,file='PCs', serv=True)
    ws['E9'].value = t_pcs
    ws['E10'].value = cortex
    ws['E11'].value = t_pcs - cortex
    t_net,cortex,vp = totalAssets(central=central,file='NET_DEV', serv=False)
    ws['E12'].value = t_net
    wb.save(des_path)
    wb.close()
    pcs_Inv(central=central,file='PCs',sheet='Inventario - PC')
    pcs_Inv(central=central,file='SERVERS',sheet='Inventario')
    eol_total = eol(central=central)

    wb = openpyxl.load_workbook(des_path)
    ws = wb[f'Resumen']
    ws['E21'].value = eol_total
    wb.save(des_path)
    wb.close()
    vuln(vulnerabilitie = 'CRITICAL', central = central, path_rep = des_path)
    vuln(vulnerabilitie = 'HIGH', central = central, path_rep = des_path)