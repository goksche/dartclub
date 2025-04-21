from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.tournament import Tournament
from app.services.ranking_logic import calculate_overall_ranking

router = APIRouter()


@router.get("/ranking/overall", tags=["Masters"])
def get_overall_ranking(
    tournament_ids: list[int] = Query(..., description="IDs der Wertungsturniere, z. B. ?tournament_ids=1&tournament_ids=2"),
    db: Session = Depends(get_db)
):
    if not tournament_ids:
        raise HTTPException(status_code=400, detail="Turnier-IDs erforderlich")

    tournaments = db.query(Tournament).filter(Tournament.id.in_(tournament_ids)).all()

    if len(tournaments) != len(tournament_ids):
        raise HTTPException(status_code=404, detail="Einige Turniere wurden nicht gefunden")

    return calculate_overall_ranking(db, tournaments)

@router.get("/ranking/overall/top", tags=["Masters"])
def get_top_n_players(
    tournament_ids: list[int] = Query(...),
    limit: int = Query(8),
    db: Session = Depends(get_db)
):
    tournaments = db.query(Tournament).filter(Tournament.id.in_(tournament_ids)).all()
    if len(tournaments) != len(tournament_ids):
        raise HTTPException(status_code=404, detail="Einige Turniere fehlen")

    ranking = calculate_overall_ranking(db, tournaments)
    return ranking[:limit]
