import json
from pathlib import Path


def convert_all_items_to_json(file_name: str):
    """
    Opens saved .txt of bank items and converts the txt formatted in TSV to a python dict and saves as .json
    :param file_name: your_snapshot.txt copied from runelite client plugin and saved as .txt
    :return:
    """
    with open(file=f"items/{file_name}.txt", mode="r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    items = []
    for line in lines[1:]:  # skip col headers
        parts = line.split("\t")
        if len(parts) != 3:
            print(f"Malformed line: {line}")
            continue

        item_id, name, quantity = parts
        items.append({
            "item_id": int(item_id),
            "item_name": name,
            "quantity": int(quantity)
        })

    items_json = json.dumps(items, indent=2)

    with open(file=f"items/{file_name}.json", mode="w", encoding="utf-8") as f:
        f.write(items_json)

    return len(items)


def read_snapshot_json(name: str):
    """
    Reads your .json file found within items directory and returns a dictionary of the data.
    :param name: name of your .json file to read within items directory
    :return: Dict
    """
    name = "items/" + name + ".json"

    with open(file=name, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def save_snapshot_json(name: str, data: dict):
    """
    Saves passed data to the name.json passed
    :param name: The name of your snapshot in items directory
    :param data: The dictionary of data you want to save within .json (Ex: {"summary": summary, "items": all_items})
    :return:
    """
    path = f"items/{name}.json"
    with open(file=path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def enter_tsv_into_db(tsv_data: str, file_name: str):
    with open(file=f"items/{file_name}.txt", mode="w", encoding="utf-8") as f:
        f.write(tsv_data)


def delete_file(file_name: str, file_type: str) -> bool:
    """
    Deletes a file from items dir if exists.
    Returns True if deleted successfully, False if not.
    :param file_name: name of file
    :param file_type: type of file(txt/json)
    :return: Bool
    """
    path = Path("items") / f"{file_name}.{file_type}"
    if path.exists():
        path.unlink()
        print(f"Deleted file: {path}")
        return True
    else:
        print(f"File not found: {path}")
        return False

