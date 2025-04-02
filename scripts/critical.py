import pandas as pd
import shutil
import csv
import os
import openpyxl
from openpyxl.styles import Alignment

def critical(central, current_date_and_time, severidad):
    print(f'🚀 Iniciando proceso para {severidad} en {central}')
    
    # Copiar el archivo CSV a la carpeta de reportes
    src_path = f'./AXONIUS_FILES/{central}/{severidad}.csv'
    dest_path = f'./ARCHIVOS_REPORTES/{central}/{current_date_and_time}/{severidad}.csv'
    shutil.copy(src_path, dest_path)
    
    # Leer el archivo CSV
    with open(src_path, encoding="utf-8") as file:
        csv_reader = csv.reader(file, delimiter=',')
        vulnerabilities = []
        devices = []
        for row in csv_reader:
            if row[0] == "Device":
                devices.append(row)
            if row[0] == "Vulnerability":
                vulnerabilities.append(row)
    
    # Procesar vulnerabilidades y dispositivos
    for col in vulnerabilities:
        del col[5:]
        del col[0]
    for col in devices:
        del col[:5]
    
    # Crear archivo Excel
    namew = f'{severidad.upper()}_SEV_{central}_{current_date_and_time}'
    name = f'./ARCHIVOS_REPORTES/{central}/{current_date_and_time}/{namew}.xlsx'
    
    read_file_product = pd.read_csv(dest_path)
    read_file_product.to_excel(name, index=None, header=True)
    os.remove(dest_path)
    
    # Modificar el archivo Excel
    wb = openpyxl.load_workbook(name)
    
    ws = wb['Sheet1']
    ws.title = namew
    
    # Agregar nueva hoja CVE
    wb.create_sheet('CVE')
    ws = wb['CVE']
    ws.append(["Adaptadores", "CVE", "Device Count", "Severity", "Description", "Adaptadores"])
    for vul in vulnerabilities:
        vul.insert(3, severidad.upper())
        vul.append(vul[0])
        ws.append(vul)
    
    # Crear hoja con dispositivos
    wb.remove(wb[namew])
    wb.create_sheet(namew)
    ws = wb[namew]
    ws.append(["Adaptadores", "CVE", "Numero de Dispositivos", "Severidad", "Descripcion", "Hostname", "IPs", "MAC", "Tipo y distribución OS", "Cortex"])
    
    for dev in devices:
        dev.insert(0, dev[5])
        dev.pop()
        dev.insert(0, dev[5])
        dev.pop()
        for vul in vulnerabilities:
            if dev[1] == vul[1]:
                dev.insert(2, vul[2])
                dev.insert(3, vul[3])
                dev.insert(4, vul[4])
        dev.append("SI" if 'paloalto' in dev[0] else "NO")
        ws.append(dev)
    
    wb.save(name)
    
    # Crear archivo CSV temporal para resumen
    csv_file_path = f'./ARCHIVOS_REPORTES/{central}/{current_date_and_time}/example.csv'
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Adaptadores", "CVE", "Numero de Dispositivos", "Severidad", "Descripcion", "Hostname", "IPs", "MAC", "Tipo y distribución OS", "Cortex"])
        writer.writerows(devices)
    
    df_devides = pd.read_csv(csv_file_path, encoding='utf-8', delimiter=',')
    de = df_devides.pivot_table(index="CVE", columns="Severidad", values="Numero de Dispositivos")
    
    with pd.ExcelWriter(name, engine="openpyxl", mode='a') as writer:
        de.to_excel(writer, sheet_name="RESUMEN")
    
    os.remove(csv_file_path)

    # Cargar el archivo de Excel
    wb = openpyxl.load_workbook(name)

    # Seleccionar la hoja llamada "HOJA1"
    ws = wb[namew]  # Aquí especificamos que trabajaremos con la hoja llamada "HOJA1"

    # Columnas objetivo y anchos
    columnas_objetivo = [1,2,3,4,5,6,7,8,9,10]
    columnas_ancho = {
        "A": 30,
        "B": 20,
        "C": 20,
        "D": 10,
        "E": 40,
        "F": 50,
        "G": 15,
        "H": 20,
        "I": 25,
        "J": 10
    }

    # Filtro para las celdas que quieres modificar
    fil = "A1:J1"

    # Iterar sobre las columnas objetivo y aplicar el ajuste de alineación "wrap_text"
    for col in columnas_objetivo:
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col, max_col=col):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True)  # Activar "Wrap Text"

    # Cambiar los anchos de las columnas
    for col, width in columnas_ancho.items():
        ws.column_dimensions[col].width = width

    # Aplicar el filtro a las celdas A1:G1
    ws.auto_filter.ref = fil



    ws = wb["RESUMEN"]  # Aquí especificamos que trabajaremos con la hoja llamada "HOJA1"

    # Columnas objetivo y anchos
    columnas_objetivo = [1,2]
    columnas_ancho = {
        "A": 20,
        "B": 20
    }

    # Filtro para las celdas que quieres modificar
    fil = "A1:B1"

    # Cambiar los anchos de las columnas
    for col, width in columnas_ancho.items():
        ws.column_dimensions[col].width = width

    # Aplicar el filtro a las celdas A1:G1
    ws.auto_filter.ref = fil





    ws = wb["CVE"]  # Aquí especificamos que trabajaremos con la hoja llamada "HOJA1"

    # Columnas objetivo y anchos
    columnas_objetivo = [1,2,3,4,5,6]
    columnas_ancho = {
        "A": 30,
        "B": 20,
        "C": 20,
        "D": 10,
        "E": 40,
        "F": 30
    }

    # Filtro para las celdas que quieres modificar
    fil = "A1:F1"

    # Iterar sobre las columnas objetivo y aplicar el ajuste de alineación "wrap_text"
    for col in columnas_objetivo:
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col, max_col=col):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True)  # Activar "Wrap Text"

    # Cambiar los anchos de las columnas
    for col, width in columnas_ancho.items():
        ws.column_dimensions[col].width = width

    # Aplicar el filtro a las celdas A1:G1
    ws.auto_filter.ref = fil


    # Guardar el archivo modificado
    wb.save(name)

    print(f'✅ Proceso finalizado: {name} creado exitosamente')