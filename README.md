
REPORTES AXONIUS
This workspace is for AXONIUS projects 
Instructions below

For MAC users #Create a virtual environment - "python -m venv reportes"

For MAC users #Activate a virtual environment - "source reportes/bin/activate"

For install all the requirements - "pip install -r requirements.txt"

Run the project with -"python scripts/main.py"

We need the following Files

 + NETWORK_DEVICES_<CENTRAL>_20032025.csv
 + PCs_<CENTRAL>_20032025.xlsx
 + TOTAL_ASSETS_<CENTRAL>_20032025.csv
 + SERVERS_<CENTRAL>_20032025.xlsx

-------- FOR SERVERS & PCs ------
Columns     Name
1           Adapters
2           Hostname
3           IPs
4           MAC
5           OS

-------- FOR SEVERITIES ------
Columns     Name
1           Adapters
2           Vuln ID
3           Device Count
4           CVE Description
5           OS
6           Preferred Host Name
7           Preferred IPs
8           Preferred MAC Address
9           Preferred OS: Type and Distribution
10          Adapter conection

