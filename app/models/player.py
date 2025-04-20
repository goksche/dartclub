from sqlalchemy import Column, Integer, String
from app.db import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    nickname = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
