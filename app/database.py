# app/database.py
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = "sqlite:///./app.db"  # Datei im Projektordner

engine = create_engine(
    DATABASE_URL,
    echo=True,          # SQL-Statements im Terminal anzeigen (zum Debuggen)
    connect_args={"check_same_thread": False},  # für SQLite + FastAPI nötig
)

def getSession() -> Generator[Session, None, None]:
    """
    Dependency für FastAPI: gibt eine DB-Session für Requests.
    """
    with Session(engine) as session:
        yield session

def initDatabase() -> None:
    """
    Erstellt alle Tabellen in der Datenbank.
    """
    from app import models  # sorgt dafür, dass alle Models registriert sind
    SQLModel.metadata.create_all(engine)
