from pydantic import BaseModel
from datetime import date
from typing import Literal

class TournamentBase(BaseModel):
    name: str
    type: Literal["spass", "wertung"]
    mode: Literal["liga", "ko", "gruppe"]
    date: date
    is_ranked: bool = False
    best_of: Literal[3, 5, 7, 9, 11] = 3

class TournamentCreate(TournamentBase):
    pass

class TournamentOut(TournamentBase):
    id: int

    class Config:
        from_attributes = True
