import json
from pathlib import Path

def get_unique_labels_with_value(value=9):
    base_path = Path(__file__).parent.parent / "AXONIUS_FILES" / "GENERAL_JSON"
    input_json = base_path / "GENERAL_ASSETS.json"
    output_json = base_path / "UNIQUE_LABELS.json"

    with open(input_json, "r", encoding="utf-8") as file:
        data = json.load(file)

    unique_labels = set()

    for asset in data:
        labels = asset.get("labels", [])
        if not isinstance(labels, list):
            continue

        for label in labels:
            if isinstance(label, str):
                unique_labels.add(label.strip().upper())

    result = {
        "unique_labels": {label: value for label in sorted(unique_labels)}
    }

    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    return result


def main():
    result = get_unique_labels_with_value(9)
    print("JSON generado correctamente:")
    print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
