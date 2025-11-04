from app.crud.database import read_latest_item_snapshot


def calculate_valuation(all_bank_items, db, selected_bank):
    total_low_value = 0
    total_mean_value = 0
    total_high_value = 0

    for item in all_bank_items:
        latest_snapshot = read_latest_item_snapshot(db=db, item_name=item.name, bank_name=selected_bank)
        if latest_snapshot:
            total_low_value += latest_snapshot.low_value_estimate
            total_mean_value += latest_snapshot.mean_value_estimate
            total_high_value += latest_snapshot.high_value_estimate

    return total_low_value, total_mean_value, total_high_value


def create_item_valuation_list(all_bank_items, db, selected_bank):
    rows = []
    for item in all_bank_items:
        snapshot = read_latest_item_snapshot(db=db, item_name=item.name, bank_name=selected_bank)
        if snapshot:
            rows.append({
                "name": item.name,
                "quantity": item.quantity,
                "low_value": int(snapshot.low_value_estimate),
                "mean_value": int(snapshot.mean_value_estimate),
                "high_value": int(snapshot.high_value_estimate),
            })

    return rows
