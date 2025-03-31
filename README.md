
REPORTES AXONIUS
This workspace is for AXONIUS projects 
Instructions below

For MAC users #Create a virtual environment - "python -m venv reportes"

For MAC users #Activate a virtual environment - "source reportes/bin/activate"

For install all the requirements - "pip install -r requirements.txt"

Run the project with -"python scripts/main.py"

Create file ".env" with following data:
    AXONIUS_URL="https://<ip>"
    AXONIUS_KEY="<key>"
    AXONIUS_SECRET="<secret>"

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
