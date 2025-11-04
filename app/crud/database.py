from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.db_entry import Bank, BankItem, PriceSnapshot


def create_bank(db: Session, name: str, created_at):
    bank = Bank(name=name, created_at=created_at)
    db.add(bank)
    db.flush()
    return bank


def create_bank_item(
        db: Session,
        bank_id: int,
        item_id: int,
        name: str,
        quantity: int,
        is_tradeable=False,
        uncharged_id=None,
        has_ornament_kit_equipped=False,
):

    bank_item = BankItem(
        bank_id=bank_id,
        item_id=item_id,
        name=name,
        quantity=quantity,
        is_tradeable=is_tradeable,
        uncharged_id=uncharged_id,
        has_ornament_kit_equipped=has_ornament_kit_equipped,
    )
    db.add(bank_item)
    db.flush()
    return bank_item


def create_price_snapshot(
        db: Session,
        bank_item_id: int,
        item_name: str,
        timestamp,
        high_value: int,
        low_value: int,
        mean_value: float,
):

    snapshot = PriceSnapshot(
        bank_item_id=bank_item_id,
        item_name=item_name,
        timestamp=timestamp,
        high_value_estimate=high_value,
        low_value_estimate=low_value,
        mean_value_estimate=mean_value,
    )
    db.add(snapshot)
    return snapshot


def read_all_items(db: Session):
    return db.query(BankItem).all()


def read_all_items_by_bank_id(db: Session, bank_id: int):
    return db.query(BankItem).filter_by(bank_id=bank_id).all()


def read_item_quantity_by_bank_item_id(db: Session, bank_item_id):
    result = db.query(BankItem.quantity).filter_by(id=bank_item_id).scalar()
    return result


def get_bank_id_by_name(db: Session, bank_name: str):
    bank = db.query(Bank).filter_by(name=bank_name).first()
    return bank.id if bank else None


def get_all_tradeable_if_uncharged_items(db: Session):
    return db.query(BankItem).filter(BankItem.uncharged_id.is_not(None)).all()


def get_all_banks(db: Session):
    banks = db.query(Bank).all()
    return banks


def get_bank_by_name(db: Session, name: str):
    return db.query(Bank).filter_by(name=name).first()


def bank_name_is_unique(db: Session, bank_name: str):
    return not db.query(Bank).filter(Bank.name.ilike(bank_name)).first()


def read_all_price_snapshots(db: Session):
    return db.query(PriceSnapshot).all()


def read_latest_item_snapshot(db: Session, item_name: str, bank_name: str):
    latest_snapshot = (
        db.query(PriceSnapshot)
        .join(PriceSnapshot.bank_item)
        .join(BankItem.bank)
        .filter(
            Bank.name == bank_name,
            PriceSnapshot.item_name == item_name
        )
        .order_by(PriceSnapshot.timestamp.desc())
        .first()
    )

    return latest_snapshot


def read_single_item_snapshots(db: Session, item_name: str, bank_name: str):
    snapshots = (
        db.query(PriceSnapshot)
        .join(PriceSnapshot.bank_item)
        .join(BankItem.bank)
        .filter(
            Bank.name == bank_name,
            PriceSnapshot.item_name == item_name
        )
        .all()
    )

    return snapshots


def get_similar_item_snapshots(db: Session, user_entry: str, bank_name: str):
    similar_items = (
        db.query(BankItem.name)
        .join(Bank)
        .filter(
            Bank.name == bank_name,
            BankItem.name.ilike(f"%{user_entry}%"))
        .distinct()
        .limit(10)
        .all()
    )

    return similar_items


def get_latest_snapshot_time(db: Session, passed_bank_id: int):
    last_snapshot_timestamp = (
        db.query(func.max(PriceSnapshot.timestamp))
        .join(PriceSnapshot.bank_item)
        .filter(BankItem.bank_id == passed_bank_id)
        .scalar()
    )
    return last_snapshot_timestamp


def delete_bank(db: Session, bank_name: str):
    bank = db.query(Bank).filter_by(name=bank_name).first()

    if not bank:
        return False

    db.delete(bank)
    db.commit()

    return True
