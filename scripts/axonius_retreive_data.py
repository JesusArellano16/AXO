import axonius_api_client as axonapi  # Importar la librería de Axonius API Client
import json  # Importar la librería JSON para manejar datos en formato JSON
import warnings  # Importar warnings para manejar advertencias
import pandas as pd
import urllib3
import os
import openpyxl
import os
from openpyxl.styles import Alignment
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter("ignore",category=Warning)  # Ignorar advertencias para evitar mensajes innecesarios en la consola


def axonius_retreive_data(connect_args,saved_query_name,saved_query_name_clean,central,current_date_and_time):
    path = r'./ARCHIVOS_REPORTES/'+central
    if not os.path.exists(path):
        os.mkdir(path)
    path = path + r'/'+current_date_and_time
    if not os.path.exists(path):
        os.mkdir(path)
    # Crear una instancia del cliente de Axonius
    client = axonapi.Connect(**connect_args)

    # Seleccionar el objeto API para dispositivos
    apiobj = client.devices

    # Obtener los dispositivos de la consulta guardada
    devices = apiobj.get_by_saved_query(saved_query_name)

    # Lista donde se almacenarán los dispositivos con datos filtrados
    clean_devices = []

    # Definir los campos específicos que se desean extraer de cada dispositivo
    clean_data = [
        "adapters",  # Adaptadores conectados al dispositivo
        "specific_data.data.hostname_preferred",  # Nombre de host preferido
        "specific_data.data.network_interfaces.ips_preferred",  # Dirección IP preferida
        "specific_data.data.network_interfaces.mac_preferred",  # Dirección MAC preferida
        "specific_data.data.os.type_distribution_preferred",  # Tipo de sistema operativo preferido
    ]

    # Recorrer la lista de dispositivos obtenidos de la consulta guardada
    for device in devices:
        clean_devices_dict = {}  # Diccionario para almacenar datos filtrados del dispositivo
        for data in clean_data:
            try:
                clean_devices_dict[data] = device[data]  # Intentar obtener el valor del campo especificado
            except:
                pass  # Si el campo no existe en el dispositivo, ignorarlo

        if "paloalto_xdr_adapter" in clean_devices_dict["adapters"]:
            clean_devices_dict["CORTEX"] = "SI"
        if 'deep_security_adapter' in clean_devices_dict["adapters"]:
            clean_devices_dict["DEEP SECURITY"] = "SI"
        if "paloalto_xdr_adapter" not in clean_devices_dict["adapters"]:
            clean_devices_dict["CORTEX"] = "NO"
        if 'deep_security_adapter' not in clean_devices_dict["adapters"]:
            clean_devices_dict["DEEP SECURITY"] = "NO"
        clean_devices.append(clean_devices_dict)  # Agregar el diccionario con los datos filtrados a la lista

    # Guardar los datos filtrados en un archivo JSON
    with open(f"{saved_query_name_clean}.json", "w") as final:
        json.dump(clean_devices, final, indent=4)  # Guardar los datos con formato JSON legible
    
    with open(f"{saved_query_name_clean}.json", "r") as file:
        data = json.load(file)

    df = pd.DataFrame(data)
    df.to_excel("datos.xlsx",index=False, engine="openpyxl")

    df1 = pd.read_excel("datos.xlsx")
    headers = {
        "adapters": "Adapter", 
        "specific_data.data.hostname_preferred": "Hostname", 
        "specific_data.data.network_interfaces.ips_preferred": "IPs", 
        "specific_data.data.network_interfaces.mac_preferred": "MAC",
        "specific_data.data.os.type_distribution_preferred": "OS"
    }
    #not_in_headers = False
    for key, value in headers.items():
        try:
            df1.rename(columns={key:value}, inplace=True)
        except:
            pass
    #df1[headers_old[0]] = df1[headers_old[0]].astype(str).str.replace(headers_old[0], headers_new[0])
    df1.to_excel("archivo_modificado.xlsx", index=False, engine="openpyxl")
    #print(not_in_headers)
    changes = {
        "[": "",
        "]": "",
        "'": "",
        ",": "\n"
    }

    df2 = pd.read_excel("archivo_modificado.xlsx")
    for key, value in headers.items():
        for k, v in changes.items():
            try:
                df2[value] = df2[value].astype(str).str.replace(k,v)
            except:
                pass
    df2.to_excel("archivo_modificado.xlsx", index=False, engine="openpyxl")



    archivo = "archivo_modificado.xlsx"
    wb = openpyxl.load_workbook(archivo)
    ws = wb.active  # Seleccionar la hoja activa
    columnas = [cell.value for cell in ws[1]]
    print(columnas)
    if "MAC" in columnas:
        print("TRUE")
        # Definir las columnas objetivo (A, C y D corresponden a índices 1, 3 y 4 en openpyxl)
        columnas_objetivo = [1, 3, 4]
        columnas_ancho = {
            "A": 30,
            "B": 50,
            "C": 20,
            "D": 20,
            "E": 20,
            "F": 10,
            "G": 17
        }
        fil = "A1:G1"
        
    else:
        # Definir las columnas objetivo (A, C y D corresponden a índices 1, 3 y 4 en openpyxl)
        columnas_objetivo = [1, 3]
        columnas_ancho = {
            "A": 30,
            "B": 50,
            "C": 20,
            "D": 10,
            "E": 17,

        }
        fil = "A1:E1"
    


    # Aplicar ajuste de texto en las columnas A, C y D (desde la fila 2 en adelante)
    for col in columnas_objetivo:
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col, max_col=col):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True)  # Activar "Wrap Text"

    for col, width in columnas_ancho.items():
        ws.column_dimensions[col].width = width
    ws.auto_filter.ref = fil
    # Guardar el archivo modificado

    namew = saved_query_name_clean + '_' + central + "_" + str(current_date_and_time)
    name = './ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/' + namew  + r'.xlsx'
    wb.save(name)
    ss = openpyxl.load_workbook(name)
    ss_sheet = ss['Sheet1']
    ss_sheet.title = namew
    ss.save(name)
    remo = saved_query_name_clean + '.json'
    os.remove('archivo_modificado.xlsx')
    os.remove('datos.xlsx')
    os.remove(remo)
