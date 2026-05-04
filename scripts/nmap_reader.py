import sys
import os
import re
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NMAP_DIR = os.path.join(BASE_DIR, "NMAP_FILES")
OUTPUT_FILE = os.path.join(NMAP_DIR, "NMAP_RESULTS.csv")

def normalize_ip(ip):
    return ip.strip().lower()

DB_FILE = os.path.join(NMAP_DIR, "db_nmap.csv")

def load_db():
    db = {}

    if not os.path.isfile(DB_FILE):
        print(f"DB file not found: {DB_FILE}")
        return db

    with open(DB_FILE, "r", encoding="utf-8-sig") as csvfile:  # 👈 clave
        reader = csv.DictReader(csvfile)

        headers = [h.strip() for h in reader.fieldnames]

        ip_col = None
        host_col = None
        mac_col = None

        for h in headers:
            h_clean = h.lower().replace(" ", "")

            if "ip" in h_clean:
                ip_col = h
            elif "hostname" in h_clean:
                host_col = h
            elif "mac" in h_clean:
                mac_col = h

        for row in reader:
            row = {k.strip(): v for k, v in row.items()}

            raw_ip = row.get(ip_col, "")
            ip = normalize_ip(raw_ip)

            if not ip:
                continue

            hostname = row.get(host_col)
            mac = row.get(mac_col)

            db[ip] = {
                "hostname": hostname.strip() if hostname else "",
                "mac": mac.strip() if mac else "",
                "serial": ""
            }

    return db

def clean_os(os_string):
    if not os_string:
        return ""

    os_string = re.sub(r"\(\d+%.*?\)", "", os_string).strip()

    if "-" in os_string:
        parts = os_string.split("-")
        last_part = parts[-1].strip()

        if re.match(r"^\d", last_part):
            base = os_string.split()[0]
            return f"{base} {last_part}"

    return os_string.strip()


def parse_nmap(file_path):
    hosts = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    blocks = content.split("Nmap scan report for ")

    for block in blocks[1:]:
        lines = block.splitlines()

        first_line = lines[0]

        hostname = ""
        ip = ""

        match = re.match(r"(.*?) \((.*?)\)", first_line)
        if match:
            hostname = match.group(1)
            ip = match.group(2)
        else:
            ip = first_line.strip()

        os_detected = ""

        for line in lines:
            if "Aggressive OS guesses:" in line:
                raw_os = line.split(":")[1].split(",")[0].strip()
                os_detected = clean_os(raw_os)
                break

        if not os_detected:
            for line in lines:
                if line.startswith("Running:"):
                    raw_os = line.split("Running:")[1].strip()
                    os_detected = clean_os(raw_os)
                    break

        hosts.append({
            "ip": ip,
            "hostname": hostname,
            "os": os_detected
        })

    return hosts


def get_existing_ips():
    existing_ips = set()

    if not os.path.isfile(OUTPUT_FILE):
        return existing_ips

    with open(OUTPUT_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_ips.add(normalize_ip(row["ip"]))

    return existing_ips


def save_to_csv(hosts):
    existing_ips = get_existing_ips()
    file_exists = os.path.isfile(OUTPUT_FILE)

    db = load_db()

    new_count = 0
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["id", "ip", "hostname", "mac", "serial", "os"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for host in hosts:
            ip = normalize_ip(host["ip"])
            if ip in existing_ips:
                continue

            db_data = db.get(ip)

            row = {
                "id": "",  
                "ip": ip,
                "hostname": (db_data.get("hostname") if db_data else "") or host.get("hostname"),
                "mac": db_data.get("mac") if db_data else "",
                "serial": db_data.get("serial") if db_data else "",
                "os": host.get("os", "")
            }

            writer.writerow(row)

            existing_ips.add(ip)
            new_count += 1

    return new_count

if __name__ == "__main__":

    if not os.path.isdir(NMAP_DIR):
        print(f"Folder does not exists: {NMAP_DIR}")
        sys.exit(1)

    txt_files = [f for f in os.listdir(NMAP_DIR) if f.endswith(".txt")]

    if not txt_files:
        print("There are no .txt in NMAP_FILES")
        sys.exit(1)

    all_hosts = []

    for file in txt_files:
        full_path = os.path.join(NMAP_DIR, file)

        hosts = parse_nmap(full_path)
        all_hosts.extend(hosts)

    added = save_to_csv(all_hosts)

    print(f"New hosts added: {added}")