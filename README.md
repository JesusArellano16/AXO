
REPORTES AXONIUS
This workspace is for AXONIUS projects 
Instructions below

For MAC users #Create a virtual environment - "python -m venv reportes"

For MAC users #Activate a virtual environment - "source reportes/bin/activate"

For install all the requirements - "pip install -r requirements.txt"

Run the project with -"python scripts/main.py"


git fetch origin
git reset --hard origin/main



Create file ".env" with following data:
    AXONIUS_URL="https://<ip>"
    AXONIUS_KEY="<key>"
    AXONIUS_SECRET="<secret>"

-------- FOR SEVERITIES ------

Edit Table
    Edit Columns
        Select All 
            Unselect <"Adapater Connections">, <"Vuln ID">, <"Device Count">, <"CVE Description">
Export CSV
    -File name: <critical>
    -Exclude parent complex objects columns
    -Include associated devices
                   Preferred Host Name
                   Preferred IPs
                   Preferred MAC Address
                   Preferred OS: Type and Distribution
                   Adapter conection



-------- FOR EOL ------
    Export CSV

-File name: <eol>
-Split by field values: <Installed Software>
-Don't split complex objects into columns: <check>