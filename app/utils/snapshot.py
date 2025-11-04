from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.crud.database import create_bank, create_bank_item, create_price_snapshot, get_bank_id_by_name
from app.crud.database import read_all_items_by_bank_id, get_latest_snapshot_time
from app.database import SessionLocal
from app.utils.file_io import read_snapshot_json
from app.utils.prices import fetch_all_item_prices, read_tradeable_if_uncharged, read_item_plus_ornament_kit


# Used in enter_all_items_current_price -> change to 0 for unlimited calls to the function
COOLDOWN = timedelta(hours=12)


def initial_enter_all_items_current_price(db: Session, file_name: str, bank_name: str = "Original_Bank"):
    """
    Parse first_snapshot.json and use fetch_all_item_prices to create SqlAlchemy objects to enter into database.
    If ID of item found in all_prices, pricing data is entered for item entry. If ID not found in all_prices,
    ID will be checked in all_tradeable_if_uncharged. If not found, ID will be checked in all_item_plus_ornament_kit.
    Last, Item will be deemed untradeable and prices will not be added.
    :param db: Session
    :param file_name: name of your .json file to write to
    :param bank_name: Title of your bank snapshot -> default = "Original_Bank
    :return: Dict -> {"summary": summary, "items": all_items}
    """

    snapshot_time = datetime.now(timezone.utc)
    all_prices = fetch_all_item_prices()["data"]
    all_items = read_snapshot_json(name=file_name)
    all_tradeable_if_uncharged = read_tradeable_if_uncharged()
    all_item_plus_ornament_kit = read_item_plus_ornament_kit()

    # Create Bank entry
    bank = create_bank(db, name=bank_name, created_at=snapshot_time)

    for item in all_items:
        item_id = str(item["item_id"])
        quantity = item.get("quantity", 1)

        bank_item = create_bank_item(
            db=db,
            bank_id=bank.id,
            item_id=item["item_id"],
            name=item["item_name"],
            quantity=quantity,
            is_tradeable=item_id in all_prices or int(item_id) == 995,
            uncharged_id=int(all_tradeable_if_uncharged[item_id]) if item_id in all_tradeable_if_uncharged else None,
            has_ornament_kit_equipped=item_id in all_item_plus_ornament_kit
        )

        # 1. Item is tradeable
        if item_id in all_prices:
            price_data = all_prices[item_id]
            high = price_data["high"] * quantity
            low = price_data["low"] * quantity

        # 2. Item is Charged thus untradeable
        elif item_id in all_tradeable_if_uncharged:
            uncharged_id = all_tradeable_if_uncharged[item_id]
            price_data = all_prices[str(uncharged_id)]
            high = price_data["high"] * quantity
            low = price_data["low"] * quantity

        # 3. Item is untradeable because it has an ornament kit equipped
        elif item_id in all_item_plus_ornament_kit:
            base_item = all_item_plus_ornament_kit[item_id]
            ornament_kit = all_item_plus_ornament_kit[f"kit_{item_id}"]

            high = (all_prices[base_item]["high"] + all_prices[ornament_kit]["high"]) * quantity
            low = (all_prices[base_item]["low"] + all_prices[ornament_kit]["low"]) * quantity

        # 4. Special Case -> Gold Coins/GP/Coins -> Named Coins
        elif int(item_id) == 995:
            high = quantity
            low = quantity

        # 5. Item is untradeable, no need to get price info for snapshot
        else:
            continue

        # Create PriceSnapshot
        mean_value = (high + low) / 2

        create_price_snapshot(
            db=db,
            bank_item_id=bank_item.id,
            item_name=bank_item.name,
            timestamp=snapshot_time,
            high_value=high,
            low_value=low,
            mean_value=mean_value
        )

    db.commit()


def enter_all_items_current_price(bank_name: str):
    """
    Uses bank_name param to determine bank_id, then reads all items associated with bank_id and creates more
    PriceSnapshots of item with current price for later comparison. Enters PriceSnapshot of item into db.
    :param bank_name: Name of bank within DB
    :return: None
    """
    snapshot_time = datetime.now(timezone.utc)
    all_prices = fetch_all_item_prices()["data"]
    all_item_plus_ornament_kit = read_item_plus_ornament_kit()

    # get bank.id from bank_name and then read all items matching bank.id
    with SessionLocal() as db:
        bank_id = get_bank_id_by_name(db=db, bank_name=bank_name)
        if bank_id is None:
            print(f"No bank found with name'{bank_name}'")
            return

        last_snapshot_time = get_latest_snapshot_time(db=db, passed_bank_id=bank_id)

        if last_snapshot_time:
            if last_snapshot_time.tzinfo is None:
                last_snapshot_time = last_snapshot_time.replace(tzinfo=timezone.utc)

            if (snapshot_time - last_snapshot_time) < COOLDOWN:
                remaining = COOLDOWN - (snapshot_time - last_snapshot_time)
                return False, remaining

        items = read_all_items_by_bank_id(db=db, bank_id=bank_id)

        for item in items:
            # print(item)
            item_id = str(item.item_id)

            if item.is_tradeable and item_id != '995':
                price_data = all_prices[item_id]
                if not price_data:
                    continue
                high = price_data["high"] * item.quantity
                low = price_data["low"] * item.quantity

            elif item.uncharged_id:
                uncharged_id = str(item.uncharged_id)
                price_data = all_prices[str(uncharged_id)]
                if not price_data:
                    continue
                high = price_data["high"] * item.quantity
                low = price_data["low"] * item.quantity

            elif item.has_ornament_kit_equipped:
                base_item = all_item_plus_ornament_kit[item_id]
                ornament_kit = all_item_plus_ornament_kit[f"kit_{item_id}"]
                if not base_item or not ornament_kit:
                    continue

                high = (all_prices[base_item]["high"] + all_prices[ornament_kit]["high"]) * item.quantity
                low = (all_prices[base_item]["low"] + all_prices[ornament_kit]["low"]) * item.quantity

            # Coins ID
            elif int(item_id) == 995:
                high = item.quantity
                low = item.quantity

            # Item is untradeable -> no snapshot needed
            else:
                continue

            mean_value_estimate = (high + low) / 2

            # print(item.id, item.name, snapshot_time, high, low, mean_value_estimate)
            create_price_snapshot(
                    db=db,
                    bank_item_id=item.id,
                    item_name=item.name,
                    timestamp=snapshot_time,
                    high_value=high,
                    low_value=low,
                    mean_value=mean_value_estimate
                )

        db.commit()

    return True, None


# Older write to current first_snapshot.json
def initial_enter_all_items_current_price_json(file_name: str, bank_name: str = "Original_Bank"):
    """
    Initial addition of fetched item prices to snapshot.json found in item directory. If ID of item found in all_prices,
    pricing data is entered for item entry. If ID not found in all_prices, ID will be checked in
    all_tradeable_if_uncharged. If not found, ID will be checked in all_item_plus_ornament_kit. Last, Item will be
    deemed untradeable and prices will not be added.
    :param file_name: name of your .json file to write to
    :param bank_name: Title of your bank snapshot -> default = "Original_Bank
    :return: Dict -> {"summary": summary, "items": all_items}
    """
    snapshot_time = datetime.now(timezone.utc).isoformat()
    all_prices = fetch_all_item_prices()["data"]
    # print(all_prices)

    all_items = read_snapshot_json(name=file_name)
    # print(all_items)

    all_tradeable_if_uncharged = read_tradeable_if_uncharged()
    all_item_plus_ornament_kit = read_item_plus_ornament_kit()

    untradeable_total = 0
    tradeable_if_uncharged = 0
    item_plus_ornament_kit = 0
    high_value_estimate = 0
    low_value_estimate = 0

    for item in all_items:
        # print(item)
        item_id = str(item["item_id"])

        # check if item is tradeable
        if item_id in all_prices:
            item["is_tradeable"] = True
            item[f"prices_{snapshot_time}"] = all_prices[item_id]
            # print(all_prices[str(item_id)])
            high_value_estimate += all_prices[item_id]['high'] * item["quantity"]
            low_value_estimate += all_prices[item_id]['low'] * item["quantity"]

        # check if item in a charged state, thus tradeable when uncharged
        elif item_id in all_tradeable_if_uncharged:
            print(f"Untradeable when charged -> {item['item_name']}: {item_id}")
            tradeable_if_uncharged += 1
            uncharged_id = all_tradeable_if_uncharged[item_id]
            item["uncharged_id"] = int(uncharged_id)  # set uncharged id to type int to match item_id typing
            item[f"prices_{snapshot_time}"] = all_prices[str(item["uncharged_id"])]
            high_value_estimate += all_prices[str(item["uncharged_id"])]['high'] * item["quantity"]
            low_value_estimate += all_prices[str(item["uncharged_id"])]['low'] * item["quantity"]
            item["is_tradeable"] = False
            print(f"Changed to tradeable id -> {item['uncharged_id']}")

        # check if item has an ornament kit equipped, get price for ornament kit + item
        elif item_id in all_item_plus_ornament_kit:
            """
            'prices_2025-10-09T06:16:46.159197+00:00': {'high': 1830, 'highTime': 1759981709, 'low': 1779, 'lowTime': 1759981505}}
            """
            item_plus_ornament_kit += 1
            print(item['item_name'])
            high_price_total = 0  # tally high prices for base item and ornament kit
            low_price_total = 0  # tally low prices for base item and ornament kit
            base_item = all_item_plus_ornament_kit[item_id]
            ornament_kit = all_item_plus_ornament_kit[f"kit_{item_id}"]

            high_price_total += all_prices[base_item]['high'] * item["quantity"]
            high_price_total += all_prices[ornament_kit]['high'] * item["quantity"]

            low_price_total += all_prices[base_item]['low'] * item["quantity"]
            low_price_total += all_prices[ornament_kit]['low'] * item["quantity"]

            print(high_price_total)
            print(low_price_total)

            high_value_estimate += high_price_total
            low_value_estimate += low_price_total

            item[f"prices_{snapshot_time}"] = {
                "base_item": all_prices[base_item],
                "ornament_kit": all_prices[ornament_kit],
            }

            item["has_ornament_kit_equipped"] = True
            item["is_tradeable"] = False

        else:
            untradeable_total += 1
            item["is_tradeable"] = False
            # print(f"{item['item_name']} not tradeable -> {item}")

    mean_value_estimate = (high_value_estimate + low_value_estimate) / 2

    summary = {
        "bank_name": bank_name,
        "total_untradeables": untradeable_total,
        "total_tradeable_if_charged": tradeable_if_uncharged,
        "total_has_ornament_kit_equipped": item_plus_ornament_kit,
        "snapshots": [snapshot_time],
        "bank_value": {
            snapshot_time: {
                "high_value_estimate": high_value_estimate,
                "low_value_estimate": low_value_estimate,
                "mean_value_estimate": mean_value_estimate
            }
        }
    }

    return {"summary": summary, "items": all_items}
