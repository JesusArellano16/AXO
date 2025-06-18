import os
import datetime as dt
from openpyxl import load_workbook
import csv
from centrales import centrales

from openpyxl.chart import LineChart, Reference
from openpyxl.utils import get_column_letter

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

    # Filtrar registros duplicados
    datos_filtrados = [fila for fila in datos if fila and fila[0] != fecha_hoy]

    # Agregar nuevo registro
    datos_filtrados.append(fila_nueva)

    # Si no hay encabezado, lo inferimos del tamaño de fila_nueva
    if not encabezado:
        encabezado = ["Date"] + [f"Value{i+1}" for i in range(len(fila_nueva)-1)]

    # Reescribir archivo
    with open(ruta_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(encabezado)
        writer.writerows(datos_filtrados)




def servers(central):
    ruta_base = "ARCHIVOS_REPORTES"
    current_date_and_time = str(dt.date.today())
    nombre_archivo = f"Reporte_Discovery_{central}_{current_date_and_time}.xlsx"
    ruta_completa = os.path.join(ruta_base, central, current_date_and_time, nombre_archivo)

    carpeta_script = os.path.dirname(os.path.realpath(__file__))
    ruta_graficas_dir = os.path.abspath(os.path.join(carpeta_script, "..", "src", "Graficas"))
    ruta_csv = os.path.join(ruta_graficas_dir, f"Servers_{central}.csv")

    # Crear carpeta si no existe
    if not os.path.exists(ruta_graficas_dir):
        print(f"La carpeta {ruta_graficas_dir} no existe. Creando...")
        os.makedirs(ruta_graficas_dir)

    if os.path.exists(ruta_completa):
        try:
            wb_origen = load_workbook(ruta_completa, data_only=True)
            if "Resumen" in wb_origen.sheetnames:
                hoja = wb_origen["Resumen"]
                valor = hoja["E5"].value
                wb_origen.close()
            else:
                print("La hoja 'Resumen' no existe.")
                return None
        except Exception as e:
            print(f"Error al abrir el archivo origen: {e}")
            return None

        fecha = current_date_and_time

        # Comprobar si el archivo CSV existe para saber si escribir encabezados
        archivo_existe = os.path.exists(ruta_csv)

        try:
            fecha_formateada = dt.date.today().strftime("%d/%m/%y")
            #encabezados = ["Fecha", "Valor E5"]
            fila_nueva = [fecha_formateada, valor]
            sobrescribir_registro_csv(ruta_csv, fila_nueva)
        except Exception as e:
            print(f"Error al escribir en el CSV: {e}")
    else:
        print(f"El archivo origen no existe: {ruta_completa}")
        return False
    

def servers_cortex(central):
    ruta_base = "ARCHIVOS_REPORTES"
    current_date_and_time = str(dt.date.today())
    nombre_archivo = f"Reporte_Discovery_{central}_{current_date_and_time}.xlsx"
    ruta_completa = os.path.join(ruta_base, central, current_date_and_time, nombre_archivo)

    carpeta_script = os.path.dirname(os.path.realpath(__file__))
    ruta_graficas_dir = os.path.abspath(os.path.join(carpeta_script, "..", "src", "Graficas"))
    ruta_csv = os.path.join(ruta_graficas_dir, f"Cortex_{central}.csv")

    # Crear carpeta si no existe
    if not os.path.exists(ruta_graficas_dir):
        print(f"La carpeta {ruta_graficas_dir} no existe. Creando...")
        os.makedirs(ruta_graficas_dir)

    if os.path.exists(ruta_completa):
        try:
            wb_origen = load_workbook(ruta_completa, data_only=True)
            if "Resumen" in wb_origen.sheetnames:
                hoja = wb_origen["Resumen"]
                servers_num = hoja["E5"].value
                servers_c = hoja["E6"].value
                wb_origen.close()
            else:
                print("La hoja 'Resumen' no existe.")
                return None
        except Exception as e:
            print(f"Error al abrir el archivo origen: {e}")
            return None

        fecha = current_date_and_time

        # Comprobar si el archivo CSV existe para saber si escribir encabezados
        archivo_existe = os.path.exists(ruta_csv)

        try:
            fecha_formateada = dt.date.today().strftime("%d/%m/%y")
            #encabezados = ["Fecha", "Valor E5", "Valor E6"]
            fila_nueva = [fecha_formateada, servers_c, servers_num - servers_c]
            sobrescribir_registro_csv(ruta_csv, fila_nueva)
        except Exception as e:
            print(f"Error al escribir en el CSV: {e}")
    else:
        print(f"El archivo origen no existe: {ruta_completa}")
        return False


def agregar_hojas_graficas(central):
    # Fecha actual
    fecha_hoy = dt.date.today().strftime("%Y-%m-%d")

    # Ruta del Excel de reporte
    ruta_reporte = os.path.join("ARCHIVOS_REPORTES", central, fecha_hoy, f"Reporte_Discovery_{central}_{fecha_hoy}.xlsx")

    # Ruta del script actual
    carpeta_script = os.path.dirname(os.path.realpath(__file__))

    # Rutas absolutas a los CSV
    ruta_csv_servers = os.path.abspath(os.path.join(carpeta_script, "..", "src", "Graficas", f"Servers_{central}.csv"))
    ruta_csv_cortex = os.path.abspath(os.path.join(carpeta_script, "..", "src", "Graficas", f"Cortex_{central}.csv"))

    # Verifica que exista el Excel
    if not os.path.exists(ruta_reporte):
        print(f"No se encontró el archivo de reporte para {central}.")
        return

    try:
        wb = load_workbook(ruta_reporte)

        def crear_hoja_con_grafica(wb, nombre_hoja, ruta_csv, columnas_numericas):
            # Elimina hoja previa si existe
            if nombre_hoja in wb.sheetnames:
                del wb[nombre_hoja]
            ws = wb.create_sheet(nombre_hoja)

            # Leer CSV y escribir en hoja
            with open(ruta_csv, newline='') as f:
                reader = csv.reader(f)
                for row_idx, row in enumerate(reader, start=1):
                    for col_idx, valor in enumerate(row, start=1):
                        # Convertir a número si es columna numérica y no es encabezado
                        if row_idx > 1 and col_idx in columnas_numericas:
                            try:
                                valor = float(valor.replace(",", "")) if isinstance(valor, str) else float(valor)
                            except:
                                pass
                        ws.cell(row=row_idx, column=col_idx).value = valor

            # Crear gráfica
            chart = LineChart()
            chart.title = f"Datos de {nombre_hoja}"
            chart.style = 2
            chart.y_axis.title = "Cantidad"
            chart.x_axis.title = "Fecha"

            if central == "IXTLA" :
                if nombre_hoja == "Grafica_Servers":
                    increments = 1000
                    min_val = 5000
                if nombre_hoja == "Grafica_Cortex":
                    increments = 500
                    min_val = 2500
            elif central == "L_ALB" :
                if nombre_hoja == "Grafica_Servers":
                    increments = 20
                    min_val = 70
                if nombre_hoja == "Grafica_Cortex":
                    increments = 10
                    min_val = 10
            elif central == "CARSO" :
                if nombre_hoja == "Grafica_Servers":
                    increments = 5
                    min_val = 20
                if nombre_hoja == "Grafica_Cortex":
                    increments = 2
                    min_val = 20
                    
            # ← Esta línea fuerza el eje Y a usar incrementos de 10
            chart.y_axis.majorUnit = increments
            chart.y_axis.scaling.min = min_val


            max_row = ws.max_row
            for col_idx in columnas_numericas:
                data = Reference(ws, min_col=col_idx, min_row=1, max_row=max_row)
                chart.add_data(data, titles_from_data=True)

            # Categorías (fechas) están en la columna A
            cats = Reference(ws, min_col=1, min_row=2, max_row=max_row)
            chart.set_categories(cats)

            # Insertar gráfica un par de columnas después de la última
            col_chart = get_column_letter(max(columnas_numericas) + 2)
            ws.add_chart(chart, f"{col_chart}2")

        # Crear hojas
        crear_hoja_con_grafica(wb, "Grafica_Servers", ruta_csv_servers, [2])
        crear_hoja_con_grafica(wb, "Grafica_Cortex", ruta_csv_cortex, [2, 3])

        wb.save(ruta_reporte)
        #print(f"Hojas 'Grafica_Servers' y 'Grafica_Cortex' agregadas correctamente a {ruta_reporte}")
    except Exception as e:
        print(f"Error al crear hojas con gráficas: {e}")




if __name__ == '__main__':
    for central in centrales:
        try:
            servers(central.nombre)
            servers_cortex(central.nombre)
            agregar_hojas_graficas(central.nombre)

        except Exception as e:
            print(f"Error : {e}")