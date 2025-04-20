from pydantic import BaseModel
from datetime import date
from typing import Literal

class TournamentBase(BaseModel):
    name: str
    type: Literal["spass", "wertung"]
    mode: Literal["liga", "ko", "gruppe"]
    date: date
    is_ranked: bool = False

class TournamentCreate(TournamentBase):
    pass

class TournamentOut(TournamentBase):
    id: int

    class Config:
        from_attributes = True
