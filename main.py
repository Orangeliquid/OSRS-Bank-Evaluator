from app.crud.database import read_all_items, read_all_price_snapshots, read_single_item_snapshots
from app.crud.database import get_all_tradeable_if_uncharged_items, get_all_banks
from app.database import init_db, SessionLocal
from app.utils.file_io import convert_all_items_to_json
from app.utils.snapshot import initial_enter_all_items_current_price, enter_all_items_current_price

# Notice -> Snapshot len will be less than total bank spots used because bank spots used counts place-holders

# todo - allow user to check items in bank with check box to track
# todo - display top 10 changes in item prices
# todo - find sprite ico for all items and add to item sql entry -> display via streamlit next to item
# todo - add logic for crystal armor -> total crystal armor seeds

# No longer needed, init_db is called within front end logic
if __name__ == '__main__':
    pass
    # file_requested = "first_snapshot"
    # bank_name = "Original_Bank"

    # first run must init db
    # init_db()

    # step 1 -> convert .txt to original json
    # convert_all_items_to_json(file_name=file_requested)

    # step 2 -> enter all current prices for items that are tradeable
    # with SessionLocal() as db:
    #     initial_enter_all_items_current_price(db=db, file_name=file_requested)

    # read all bank items
    # with SessionLocal() as db:
    #     items = read_all_items(db=db)
    #     for item in items:
    #         print(item.name, item.quantity, item.is_tradeable, item.bank.name)
    #     print(len(items))

    # read all price snapshots
    # with SessionLocal() as db:
    #     snapshots = read_all_price_snapshots(db=db)
    #     for snapshot in snapshots:
    #         print("---")
    #         print(snapshot.timestamp)
    #         print(snapshot.item_name)
    #         print(snapshot.low_value_estimate, snapshot.high_value_estimate, snapshot.mean_value_estimate)
    #         print("---")

    # step 3 -> In the future, get current pricing of items from file_requested and add snapshot data to each entry
    # enter_all_items_current_price(bank_name=bank_name)

    # step 4 -> look at two snapshots
    # item_to_query = "Confliction gauntlets"
    # with SessionLocal() as db:
    #     snapshots = read_single_item_snapshots(db=db, item_name=item_to_query)
    #     for snapshot in snapshots:
    #         print("------")
    #         print(snapshot.timestamp, snapshot.item_name)
    #         print(snapshot.low_value_estimate, snapshot.mean_value_estimate, snapshot.high_value_estimate)
    #         print("------")

    # Query Uncharged IDs
    # with SessionLocal() as db:
    #     all_tradeable_if_uncharged = get_all_tradeable_if_uncharged_items(db=db)
    #     for item in all_tradeable_if_uncharged:
    #         print(item.uncharged_id, item.name)

    # Query all banks
    # with SessionLocal() as db:
    #     all_banks = get_all_banks(db=db)
    #     for bank in all_banks:
    #         print(bank.name)
