import pandas as pd
import shutil
import os
import openpyxl

def networks(central, current_date_and_time):
    shutil.copy('./AXONIUS_FILES/network.csv','./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/network.csv')
    csv_file_path = './ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/network.csv'
    df = pd.read_csv(csv_file_path)

    # Rename columns
    df = df.rename(columns={'Aggregated: Adapter Connections': 'Adapters',
                            'Aggregated: Asset Name': 'Asset Name',
                            'Aggregated: Adapter Connection Label': 'Conection Label',
                            'Aggregated: Preferred Domain': 'Preferred Domain',
                            'Aggregated: Preferred Host Name': 'Preferred Host Name',
                            'Aggregated: Domain': 'Domain',
                            'Aggregated: Host Name': 'Hostname',
                            'Aggregated: Last Seen': 'Last Seen', 
                            'Aggregated: Network Interfaces: Manufacturer': 'Network Interfaces: Manufacturer',
                            'Aggregated: Network Interfaces: MAC': 'MAC', 
                            'Aggregated: Network Interfaces: IPs': 'IPs',
                            'Aggregated: Preferred IPv4': 'Preferred IPv4',
                            'Aggregated: OS: Type': 'OS',
                            'Aggregated: Preferred OS: Type': 'Preferred OS',
                            'Aggregated: OS: Distribution': 'OS Distribution',
                            'Aggregated: Preferred OS: Distribution': 'Preferred OS Distribution',
                            'Aggregated: OS: Build': 'OS: Build',
                            'Aggregated: Preferred OS: Build': 'Preferred OS: Build',
                            'Aggregated: OS: Full OS String': 'Full OS String',
                            'Aggregated: Preferred Device Manufacturer': 'Preferred Device Manufacturer',
                            'Aggregated: Preferred Device Model': 'Preferred Device Model',
                            'Aggregated: Device Manufacturer Serial': 'Device Manufacturer Serial',
                            'Aggregated: Tags': 'Tag',
                            'Aggregated: Preferred User': 'Preferred User',
                            'Aggregated: Latest Used User': 'Lastest Used User',
                            'Aggregated: Latest Used User Email': 'Latest Used User Email'})
    
    df.to_csv(csv_file_path, index=False)
    shutil.copy('./AXONIUS_FILES/assets.csv','./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/assets.csv')
    csv_file_path1 = './ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/assets.csv'
    df = pd.read_csv(csv_file_path1)

    # Rename columns
       # Rename columns
    df = df.rename(columns={'Aggregated: Adapter Connections': 'Adapters',
                            'Aggregated: Asset Name': 'Asset Name',
                            'Aggregated: Adapter Connection Label': 'Conection Label',
                            'Aggregated: Preferred Domain': 'Preferred Domain',
                            'Aggregated: Preferred Host Name': 'Preferred Host Name',
                            'Aggregated: Domain': 'Domain',
                            'Aggregated: Host Name': 'Hostname',
                            'Aggregated: Last Seen': 'Last Seen', 
                            'Aggregated: Network Interfaces: Manufacturer': 'Network Interfaces: Manufacturer',
                            'Aggregated: Network Interfaces: MAC': 'MAC', 
                            'Aggregated: Network Interfaces: IPs': 'IPs',
                            'Aggregated: Preferred IPv4': 'Preferred IPv4',
                            'Aggregated: OS: Type': 'OS',
                            'Aggregated: Preferred OS: Type': 'Preferred OS',
                            'Aggregated: OS: Distribution': 'OS Distribution',
                            'Aggregated: Preferred OS: Distribution': 'Preferred OS Distribution',
                            'Aggregated: OS: Build': 'OS: Build',
                            'Aggregated: Preferred OS: Build': 'Preferred OS: Build',
                            'Aggregated: OS: Full OS String': 'Full OS String',
                            'Aggregated: Preferred Device Manufacturer': 'Preferred Device Manufacturer',
                            'Aggregated: Preferred Device Model': 'Preferred Device Model',
                            'Aggregated: Device Manufacturer Serial': 'Device Manufacturer Serial',
                            'Aggregated: Tags': 'Tag',
                            'Aggregated: Preferred User': 'Preferred User',
                            'Aggregated: Latest Used User': 'Lastest Used User',
                            'Aggregated: Latest Used User Email': 'Latest Used User Email'})

    df.to_csv(csv_file_path1, index=False)
    namew = 'NET_DEV_' + central + "_" + str(current_date_and_time)
    name = './ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/' + namew  + '.xlsx'
    read_file_product = pd.read_csv ('./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/network.csv')
    read_file_product.to_excel (name, index = None, header=True)

    os.remove('./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/network.csv')

    ss = openpyxl.load_workbook(name)
    ss_sheet = ss['Sheet1']
    ss_sheet.title = namew
    ss.save(name)

    namew = 'TOTAL_ASSETS_' + central + "_" + str(current_date_and_time)
    name = './ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/' + namew  + '.xlsx'
    read_file_product = pd.read_csv ('./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/assets.csv')
    read_file_product.to_excel (name, index = None, header=True)

    os.remove('./ARCHIVOS_REPORTES/'+central+'/'+current_date_and_time+'/assets.csv')

    ss = openpyxl.load_workbook(name)
    ss_sheet = ss['Sheet1']
    ss_sheet.title = namew
    ss.save(name)