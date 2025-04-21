from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RankingSnapshot(Base):
    __tablename__ = "ranking_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    tournament_ids = Column(String)  # Kommagetrennte Liste
    json_data = Column(Text)         # Gespeichertes Ranking als JSON
