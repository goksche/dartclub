from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse, JSONResponse
import csv
import io
from app.db import get_db
from app.models.tournament import Tournament
from app.models.player import Player
from app.models.match import Match
from app.schemas.tournament import TournamentCreate, TournamentOut
from app.crud import tournament as crud
from app.crud.player import get_all_players, get_player_by_id
from app.crud.tournament import add_player_to_tournament
from app.services.group_logic import (
    generate_grouped_round_robin_matches,
    calculate_ranking,
    start_defined_ko_bracket
)
from app.services.ko_logic import generate_ko_matches

router = APIRouter()


@router.get("/ping", tags=["Turniere"])
def ping():
    return {"status": "🏁 Turnier-Modul bereit"}


@router.post("/", response_model=TournamentOut, tags=["Turniere"])
def create(tournament: TournamentCreate, db: Session = Depends(get_db)):
    return crud.create_tournament(db, tournament)


@router.get("/{tournament_id}/ranking", tags=["Turniere"])
def get_ranking(tournament_id: int, db: Session = Depends(get_db)):
    players = get_all_players(db)
    return calculate_ranking(db, tournament_id, players)


@router.post("/{tournament_id}/start", tags=["Turniere"])
def start_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    players = tournament.players
    seeded = getattr(tournament, "seeded_players", [])

    if tournament.mode == "liga":
        generate_round_robin_matches(db, tournament, players)
        return {"status": "Liga-Spielplan generiert", "mode": "liga"}

    if tournament.mode == "ko":
        generate_ko_matches(db, tournament, players)
        return {"status": "KO-Spielplan generiert", "mode": "ko"}

    if tournament.mode == "gruppe":
        groups = generate_grouped_round_robin_matches(db, tournament, players, seeded)
        return {"status": "Gruppen-Spielplan generiert", "groups": groups}

    return {"status": "Modus nicht implementiert", "mode": tournament.mode}


@router.post("/{tournament_id}/add-player/{player_id}", tags=["Turniere"])
def add_player(tournament_id: int, player_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    player = get_player_by_id(db, player_id)
    if not tournament or not player:
        raise HTTPException(status_code=404, detail="Turnier oder Spieler nicht gefunden")
    return add_player_to_tournament(db, tournament, player)


@router.get("/{tournament_id}/status", tags=["Turniere"])
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


@router.get("/{tournament_id}/winner", tags=["Turniere"])
def get_winner(tournament_id: int, db: Session = Depends(get_db)):
    matches = db.query(Match).filter(Match.tournament_id == tournament_id).all()
    final_match = max(matches, key=lambda m: m.round, default=None)

    if final_match and final_match.legs_player1 is not None and final_match.legs_player2 is not None:
        if final_match.legs_player1 > final_match.legs_player2:
            return {"winner_id": final_match.player1_id}
        else:
            return {"winner_id": final_match.player2_id}
    return {"status": "Kein Finaler Sieger ermittelt"}


@router.post("/{tournament_id}/start-ko", tags=["Turniere"])
def start_ko_from_groups(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    players = tournament.players
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    return start_defined_ko_bracket(db, tournament, players)


@router.get("/{tournament_id}/bracket", tags=["Turniere"])
def get_bracket(tournament_id: int, db: Session = Depends(get_db)):
    matches = db.query(Match).filter(Match.tournament_id == tournament_id).order_by(Match.round).all()
    bracket = {}
    for match in matches:
        round_name = f"Runde {match.round}"
        if round_name not in bracket:
            bracket[round_name] = []
        bracket[round_name].append({
            "match_id": match.id,
            "player1": match.player1.nickname if match.player1 else None,
            "player2": match.player2.nickname if match.player2 else None,
            "legs": f"{match.legs_player1}:{match.legs_player2}" if match.legs_player1 is not None else "offen"
        })
    return bracket


@router.get("/{tournament_id}/ranking-live", tags=["Turniere"])
def get_live_ranking(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")
    players = tournament.players
    return calculate_ranking(db, tournament.id, players)


@router.get("/{tournament_id}/ranking-grouped", tags=["Turniere"])
def get_grouped_ranking(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")
    players = tournament.players
    ranking = calculate_ranking(db, tournament.id, players)

    grouped = {}
    for player in ranking:
        group = player.get("group", "Unknown")
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(player)

    return grouped


@router.get("/{tournament_id}/export/ranking.csv", tags=["Turniere"])
def export_ranking_csv(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")
    players = tournament.players
    ranking = calculate_ranking(db, tournament.id, players)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["position", "group", "nickname", "points", "leg_diff", "wins", "losses"])
    writer.writeheader()
    for r in ranking:
        writer.writerow(r)

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=ranking.csv"})


@router.get("/{tournament_id}/export/ranking.json", tags=["Turniere"])
def export_ranking_json(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")
    players = tournament.players
    ranking = calculate_ranking(db, tournament.id, players)
    return JSONResponse(content=ranking)

@router.get("/{tournament_id}/bracket-frontend", tags=["Turniere"])
def get_bracket_frontend(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    matches = db.query(Match).filter(Match.tournament_id == tournament_id).order_by(Match.round).all()
    rounds = {}

    for match in matches:
        if match.round not in rounds:
            rounds[match.round] = []

        rounds[match.round].append({
            "id": match.id,
            "player1": match.player1.nickname if match.player1 else None,
            "player2": match.player2.nickname if match.player2 else None,
            "score": (
                f"{match.legs_player1}:{match.legs_player2}"
                if match.legs_player1 is not None and match.legs_player2 is not None
                else None
            )
        })

    formatted = {
        "tournament": tournament.name,
        "rounds": [
            {
                "name": get_round_name(round_number),
                "matches": matches
            }
            for round_number, matches in sorted(rounds.items())
        ]
    }

    return formatted


def get_round_name(round_number: int) -> str:
    names = {
        1: "Viertelfinale",
        2: "Halbfinale",
        3: "Finale"
    }
    return names.get(round_number, f"Runde {round_number}")
