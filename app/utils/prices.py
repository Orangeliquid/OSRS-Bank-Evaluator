import requests
import json
import json5
import os
import time


CACHE_FILE = "cache/prices_cache.json"
CACHE_DURATION = 60 * 60 * 3  # 3 hours


def fetch_all_item_prices():
    """
    Fetches all tradeable OSRS item prices from runescape api, saves cached data within cache directory in .json.
    Uses cache from last get request if called within cache duration.
    """
    # Create cache dir if missing
    os.makedirs("cache", exist_ok=True)

    # Check if cache exist and is recent
    if os.path.exists(CACHE_FILE):
        with open(file=CACHE_FILE, mode="r", encoding="utf-8") as f:
            cache = json.load(f)

            if time.time() - cache["timestamp"] < CACHE_DURATION:
                print("Using cached prices..")
                return cache["data"]

    # Else fetch new data
    url = "https://prices.runescape.wiki/api/v1/osrs/latest"
    response = requests.get(url, headers={"User-Agent": "OBVA/1.0"})  # OBVA -> Orangeliquid Bank Value App
    data = response.json()

    with open(file=CACHE_FILE, mode="w", encoding="utf-8") as f:
        json.dump({"timestamp": time.time(), "data": data}, f)

    return data


# json5 for inline comment handling for tradeable_if_uncharged.json and item_plus_ornament_kit.json
def read_tradeable_if_uncharged():
    """
    Opens and reads items/tradeable_if_uncharged.json, then returns data in a dictionary
    :return: Dict
    """
    with open(file="items/tradeable_if_uncharged.json", mode="r", encoding="utf-8") as f:
        data = json5.load(f)

    return data


def read_item_plus_ornament_kit():
    """
    Opens and reads items/item_plus_ornament_kit.json, then returns data in a dictionary
    :return: Dict
    """
    with open(file="items/item_plus_ornament_kit.json", mode="r", encoding="utf-8") as f:
        data = json5.load(f)

    return data

