from sqlalchemy.orm import Session
from app.models.tournament import Tournament
from app.schemas.tournament import TournamentCreate

def create_tournament(db: Session, tournament: TournamentCreate):
    db_tournament = Tournament(**tournament.dict())
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament
