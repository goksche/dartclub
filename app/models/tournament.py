from sqlalchemy import Column, Integer, String, Boolean, Date
from app.db import Base

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # spass | wertung
    mode = Column(String, nullable=False)  # liga | ko | gruppe
    date = Column(Date, nullable=False)
    is_ranked = Column(Boolean, default=False)
