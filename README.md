
REPORTES AXONIUS
This workspace is for AXONIUS projects 
Instructions below

For MAC users #Create a virtual environment - "python -m venv reportes"

For MAC users #Activate a virtual environment - "source reportes/bin/activate"

For install all the requirements - "pip install -r requirements.txt"

Run the prohect with -"Reportes"
Add Central with -"Add_Central"
Remove Central with -"Remove_Central"
List Centrals names with -"Show_Centrals"


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
    -Don't split complex objects into columns
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



For alias Reportes
Open terminal
    nano ~/.zshrc
    Reportes() {
    python /Users/jesusarellano/Documents/TELCEL/AXONIUS/Desarrollo/scripts/prep_Central.py "$@" && \
    python /Users/jesusarellano/Documents/TELCEL/AXONIUS/Desarrollo/scripts/main.py
    }
    CTRL+O, Enter, CTRL+X
    source ~/.zshrc

For alias Add_Central
Open terminal
    nano ~/.zshrc
    alias Add_Central="python3 /Users/jesusarellano/Documents/TELCEL/AXONIUS/Desarrollo/scripts/add_Central.py"
    CTRL+O, Enter, CTRL+X
    source ~/.zshrc

For alias Remove_Central
Open terminal
    nano ~/.zshrc
    alias Remove_Central="python3 /Users/jesusarellano/Documents/TELCEL/AXONIUS/Desarrollo/scripts/remove_central.py"
    CTRL+O, Enter, CTRL+X
    source ~/.zshrc

For alias Show_Centrals
Open terminal
    nano ~/.zshrc
    alias Show_Centrals="python3 /Users/jesusarellano/Documents/TELCEL/AXONIUS/Desarrollo/scripts/show_Central.py"
    CTRL+O, Enter, CTRL+X
    source ~/.zshrc