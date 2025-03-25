import pandas as pd
import shutil
import csv
import os
import openpyxl

def critical(central, current_date_and_time,severidad):
    shutil.copy('./AXONIUS_FILES/'+severidad+'.csv','./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+"/"+severidad+'.csv')
    with open('./AXONIUS_FILES/'+severidad+'.csv', encoding="utf-8") as file:
        csv_reader = csv.reader(file, delimiter=',')
        vulnerabilities = []
        devices =[]
        for row in csv_reader:
            if row[0] == "Device":
                devices.append(row)
            if row[0] == "Vulnerability":
                vulnerabilities.append(row)
    for col in vulnerabilities:
        del col[5:]
        del col[0]
    for col in devices:
        del col[:5]
    namew = severidad.upper()+'_SEV_' + central + "_" + str(current_date_and_time)
    name = r'./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+"/" + namew  + r'.xlsx'
    read_file_product = pd.read_csv (r'./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+"/"+severidad+r'.csv')
    read_file_product.to_excel (name, index = None, header=True)
    os.remove(r'./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+"/"+severidad+r'.csv')

    wb = openpyxl.load_workbook(name)
    ws = wb['Sheet1']
    ws.title = namew
    wb.create_sheet('CVE')
    ws = wb['CVE']
    ws.append(["Adaptadores","CVE","Device Count","Severity","Description","Adaptadores"])
    for vul in vulnerabilities:
        vul.insert(3,severidad.upper())
        vul.append(vul[0])
        ws.append(vul)
    wb.remove(wb[namew])
    wb.create_sheet(namew)
    ws = wb[namew]
    ws.append(["Adaptadores","CVE","Numero de Dispositivos","Severidad","Descripcion","Hostname","IPs","MAC","Tipo y distribución OS","Cortex"])
    for dev in devices:
        dev.insert(0,dev[5])
        dev.pop()
        dev.insert(0,dev[5])
        dev.pop()
        for vul in vulnerabilities:
            if dev[1]== vul[1]:
                dev.insert(2,vul[2])
                dev.insert(3,vul[3])
                dev.insert(4,vul[4])
        if 'paloalto' in dev[0]:
            dev.append("SI")
        if not 'paloalto' in dev[0]:
            dev.append("NO")
        ws.append(dev)

    wb.save(name)


    devices.insert(0,["Adaptadores","CVE","Numero de Dispositivos","Severidad","Descripcion","Hostname","IPs","MAC","Tipo y distribución OS","Cortex"])
    
    csv_file_path='./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+"/"+'example.csv'
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(devices)
    df_devides = pd.read_csv(csv_file_path,encoding='utf-8',delimiter=',')
    de=df_devides.pivot_table(index="CVE",columns="Severidad",values="Numero de Dispositivos")
    
    with pd.ExcelWriter(name,engine="openpyxl", mode='a') as writer:
        de.to_excel(writer,sheet_name="RESUMEN")
    os.remove(r'./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+"/"+r'example.csv')
