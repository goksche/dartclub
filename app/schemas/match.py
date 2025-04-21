from pydantic import BaseModel

class MatchReport(BaseModel):
    legs_player1: int
    legs_player2: int

class MatchOut(BaseModel):
    id: int
    tournament_id: int
    player1_id: int
    player2_id: int
    legs_player1: int
    legs_player2: int
    best_of: int

    class Config:
        from_attributes = True
