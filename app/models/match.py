from sqlalchemy import Column, Integer, ForeignKey
from app.db import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    player1_id = Column(Integer, ForeignKey("players.id"))
    player2_id = Column(Integer, ForeignKey("players.id"))
    legs_player1 = Column(Integer, default=0)
    legs_player2 = Column(Integer, default=0)
    round = Column(Integer, default=1)
    best_of = Column(Integer, default=3)
