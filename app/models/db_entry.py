from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Bank(Base):
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    items = relationship(
        "BankItem",
        back_populates="bank",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class BankItem(Base):
    __tablename__ = "bank_items"

    id = Column(Integer, primary_key=True)
    bank_id = Column(
        Integer,
        ForeignKey("banks.id", ondelete="CASCADE"),
        index=True,
    )
    item_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    is_tradeable = Column(Boolean, default=False)
    uncharged_id = Column(Integer, nullable=True)
    has_ornament_kit_equipped = Column(Boolean, default=False)

    bank = relationship("Bank", back_populates="items")
    price_snapshots = relationship(
        "PriceSnapshot",
        back_populates="bank_item",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True)
    bank_item_id = Column(
        Integer,
        ForeignKey("bank_items.id", ondelete="CASCADE"),
    )
    item_name = Column(String)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    high_value_estimate = Column(Integer)
    low_value_estimate = Column(Integer)
    mean_value_estimate = Column(Float)

    bank_item = relationship("BankItem", back_populates="price_snapshots")
