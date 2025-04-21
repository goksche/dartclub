from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./dartclub.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.models.snapshot import RankingSnapshot

# Nur bei Bedarf einmal ausführen – z. B. im Startscript oder interaktiv
def init_snapshot_table():
    Base.metadata.create_all(bind=engine)
