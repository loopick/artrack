import json
from pathlib import Path

ADDRESS_FILE = Path("addresses.json")

def load_addresses():
    """Загружает адреса и имена из JSON-файла"""
    if ADDRESS_FILE.exists():
        with open(ADDRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_addresses(addresses):
    """Сохраняет адреса и имена в JSON-файл"""
    with open(ADDRESS_FILE, "w") as f:
        json.dump(addresses, f, indent=2)

def add_address(address, name=""):
    """Добавляет новый адрес с именем"""
    addresses = load_addresses()
    addresses[address] = name  # Сохраняем имя
    save_addresses(addresses)
    return True

def remove_address(address):
    """Удаляет адрес, если он есть в списке"""
    addresses = load_addresses()
    if address in addresses:
        del addresses[address]
        save_addresses(addresses)
        return True
    return False
