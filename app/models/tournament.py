from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


tournament_players = Table(
    "tournament_players",
    Base.metadata,
    Column("tournament_id", ForeignKey("tournaments.id")),
    Column("player_id", ForeignKey("players.id")),
)

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    is_ranked = Column(Boolean, default=False)
    best_of = Column(Integer, default=3)
    players = relationship("Player", secondary=tournament_players, backref="tournaments")
