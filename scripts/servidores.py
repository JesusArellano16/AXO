import pandas as pd
import shutil
import csv
import os
import openpyxl

def servers(central, current_date_and_time):
    cortex = []
    trendMicro = []
    shutil.copy('./AXONIUS_FILES/servers.csv','./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/servers.csv')
    # Reading the CSV file into a DataFrame
    csv_file_path = './ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/servers.csv'
    df = pd.read_csv(csv_file_path)

    # Rename columns
    df = df.rename(columns={'Aggregated: Adapter Connections': 'Adapters',
                            'Aggregated: Preferred Host Name': 'Hostname',
                            'Aggregated: Preferred IPs': 'IPs', 
                            'Aggregated: Preferred MAC Address': 'MAC', 
                            'Aggregated: Preferred OS: Type and Distribution': 'OS'})


    with open('./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/servers.csv') as csvfile:
        file = csv.reader(csvfile,delimiter=',')
        a = 0
        for row in file:
            if a>0:
                if 'paloalto' in row[0]:
                    cortex.append("SI")
                if 'deep_security' in row[0]:
                    trendMicro.append("SI")
                if not 'paloalto' in row[0]:
                    cortex.append("NO")
                if not 'deep_security' in row[0]:
                    trendMicro.append("NO")
            a = a + 1

        df['Cortex'] = cortex
        df['Virtual Patching'] = trendMicro
        df.to_csv(csv_file_path, index=False)

    namew = 'SERVERS_' + central + "_" + str(current_date_and_time)
    name = './ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/' + namew  + r'.xlsx'
    read_file_product = pd.read_csv ('./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/servers.csv')
    read_file_product.to_excel (name, index = None, header=True)

    os.remove('./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/servers.csv')

    ss = openpyxl.load_workbook(name)
    ss_sheet = ss['Sheet1']
    ss_sheet.title = namew
    ss.save(name)