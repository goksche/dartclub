from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.tournament import Tournament
from app.models.player import Player
from app.models.match import Match
from app.schemas.tournament import TournamentCreate, TournamentOut
from app.crud import tournament as crud
from app.crud.player import get_all_players, get_player_by_id
from app.crud.tournament import add_player_to_tournament
from app.services.group_logic import generate_round_robin_matches, calculate_ranking
from app.services.ko_logic import generate_ko_matches

router = APIRouter()

# Healthcheck
@router.get("/ping")
def ping():
    return {"status": "🏁 Turnier-Modul bereit"}

# Turnier erstellen
@router.post("/", response_model=TournamentOut)
def create(tournament: TournamentCreate, db: Session = Depends(get_db)):
    return crud.create_tournament(db, tournament)

# Ranking (Liga)
@router.get("/{tournament_id}/ranking")
def get_ranking(tournament_id: int, db: Session = Depends(get_db)):
    players = get_all_players(db)
    return calculate_ranking(db, tournament_id, players)

# Turnier starten (Liga oder KO)
@router.post("/{tournament_id}/start")
def start_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    players = tournament.players  # Spieler aus Beziehung holen

    if tournament.mode == "liga":
        generate_round_robin_matches(db, tournament, players)
        return {"status": "Liga-Spielplan generiert", "mode": "liga"}

    if tournament.mode == "ko":
        generate_ko_matches(db, tournament, players)
        return {"status": "KO-Spielplan generiert", "mode": "ko"}

    return {"status": "Modus nicht implementiert", "mode": tournament.mode}

# Spieler zu Turnier hinzufügen
@router.post("/{tournament_id}/add-player/{player_id}")
def add_player(tournament_id: int, player_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    player = get_player_by_id(db, player_id)
    if not tournament or not player:
        raise HTTPException(status_code=404, detail="Turnier oder Spieler nicht gefunden")
    return add_player_to_tournament(db, tournament, player)

# KO-Runden-Status anzeigen
@router.get("/{tournament_id}/status")
def tournament_status(tournament_id: int, db: Session = Depends(get_db)):
    matches = db.query(Match).filter(Match.tournament_id == tournament_id).all()
    if not matches:
        return {"status": "Noch kein Spielplan generiert"}

    rounds = set([m.round for m in matches if m.round is not None])
    latest_round = max(rounds, default=1)

    return {
        "runden": sorted(list(rounds)),
        "aktuelle_ko_runde": latest_round
    }

# Sieger des KO-Turniers ermitteln
@router.get("/{tournament_id}/winner")
def get_winner(tournament_id: int, db: Session = Depends(get_db)):
    matches = db.query(Match).filter(Match.tournament_id == tournament_id).all()
    final_match = max(matches, key=lambda m: m.round, default=None)

    if final_match and final_match.legs_player1 is not None and final_match.legs_player2 is not None:
        if final_match.legs_player1 > final_match.legs_player2:
            return {"winner_id": final_match.player1_id}
        else:
            return {"winner_id": final_match.player2_id}
    return {"status": "Kein Finaler Sieger ermittelt"}
