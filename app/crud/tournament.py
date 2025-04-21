from sqlalchemy.orm import Session
from app.models.tournament import Tournament
from app.models.player import Player
from app.schemas.tournament import TournamentCreate

# Turnier erstellen
def create_tournament(db: Session, tournament: TournamentCreate):
    db_tournament = Tournament(**tournament.dict())
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

# Spielerliste im Turnier abspeichern
def add_player_to_tournament(db: Session, tournament: Tournament, player: Player):
    if player not in tournament.players:
        tournament.players.append(player)
        db.commit()
    return tournament