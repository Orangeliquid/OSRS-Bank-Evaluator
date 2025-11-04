from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
import sqlite3

Base = declarative_base()

engine = create_engine("sqlite:///Bank_Data.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def init_db():
    Base.metadata.create_all(bind=engine)
