import sys
import os
import re
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NMAP_DIR = os.path.join(BASE_DIR, "NMAP_FILES")
OUTPUT_FILE = os.path.join(NMAP_DIR, "NMAP_RESULTS.csv")


def clean_os(os_string):
    if not os_string:
        return ""

    # Quitar porcentaje (ej: (97%))
    os_string = re.sub(r"\(\d+%.*?\)", "", os_string).strip()

    # Manejar rangos tipo "Linux 3.1 - 3.2"
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

        # --- IP y hostname ---
        first_line = lines[0]

        hostname = ""
        ip = ""

        match = re.match(r"(.*?) \((.*?)\)", first_line)
        if match:
            hostname = match.group(1)
            ip = match.group(2)
        else:
            ip = first_line.strip()

        # --- OS ---
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
    """Leer IPs ya existentes en el CSV"""
    existing_ips = set()

    if not os.path.isfile(OUTPUT_FILE):
        return existing_ips

    with open(OUTPUT_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_ips.add(row["ip"])

    return existing_ips


def save_to_csv(hosts):
    existing_ips = get_existing_ips()
    file_exists = os.path.isfile(OUTPUT_FILE)

    new_count = 0

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["ip", "hostname", "os"])

        if not file_exists:
            writer.writeheader()

        for host in hosts:
            ip = host["ip"]

            # 🔹 NO duplicar
            if ip in existing_ips:
                continue

            writer.writerow(host)
            existing_ips.add(ip)
            new_count += 1

    return new_count


if __name__ == "__main__":

    if not os.path.isdir(NMAP_DIR):
        print(f"No existe el directorio: {NMAP_DIR}")
        sys.exit(1)

    txt_files = [f for f in os.listdir(NMAP_DIR) if f.endswith(".txt")]

    if not txt_files:
        print("No hay archivos .txt en NMAP_FILES")
        sys.exit(1)

    all_hosts = []

    for file in txt_files:
        full_path = os.path.join(NMAP_DIR, file)
        print(f"Procesando: {file}")

        hosts = parse_nmap(full_path)
        all_hosts.extend(hosts)

    added = save_to_csv(all_hosts)

    print(f"\nArchivos procesados: {len(txt_files)}")
    print(f"Hosts nuevos agregados: {added}")