from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.tournament import TournamentCreate, TournamentOut
from app.crud import tournament as crud
from app.db import get_db

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "🏁 Turnier-Modul bereit"}

@router.post("/", response_model=TournamentOut)
def create(tournament: TournamentCreate, db: Session = Depends(get_db)):
    return crud.create_tournament(db, tournament)

from app.services.group_logic import calculate_ranking
from app.crud.player import get_all_players

@router.get("/{tournament_id}/ranking")
def get_ranking(tournament_id: int, db: Session = Depends(get_db)):
    players = get_all_players(db)
    return calculate_ranking(db, tournament_id, players)

from fastapi import HTTPException
from app.services.group_logic import generate_round_robin_matches
from app.crud.player import get_all_players
from app.models.tournament import Tournament

@router.post("/{tournament_id}/start")
def start_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    players = get_all_players(db)

    if tournament.mode == "liga":
        generate_round_robin_matches(db, tournament, players)
        return {"status": "Liga-Spielplan generiert", "mode": "liga"}

    return {"status": "Modus nicht implementiert", "mode": tournament.mode}
