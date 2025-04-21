from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.snapshot import RankingSnapshot
from app.models.tournament import Tournament
from app.services.ranking_logic import calculate_overall_ranking
import json

router = APIRouter()

@router.post("/ranking/snapshot", tags=["Masters"])
def create_snapshot(
    name: str,
    tournament_ids: list[int] = Query(...),
    db: Session = Depends(get_db)
):
    tournaments = db.query(Tournament).filter(Tournament.id.in_(tournament_ids)).all()
    if len(tournaments) != len(tournament_ids):
        raise HTTPException(status_code=404, detail="Einige Turniere fehlen")

    ranking = calculate_overall_ranking(db, tournaments)

    snapshot = RankingSnapshot(
        name=name,
        tournament_ids=",".join(map(str, tournament_ids)),
        json_data=json.dumps(ranking)
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return {"status": "Snapshot gespeichert", "id": snapshot.id}


@router.get("/ranking/snapshots", tags=["Masters"])
def list_snapshots(db: Session = Depends(get_db)):
    return db.query(RankingSnapshot).order_by(RankingSnapshot.created_at.desc()).all()


@router.get("/ranking/snapshot/{snapshot_id}", tags=["Masters"])
def get_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    snapshot = db.query(RankingSnapshot).filter(RankingSnapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot nicht gefunden")

    return {
        "id": snapshot.id,
        "name": snapshot.name,
        "created_at": snapshot.created_at,
        "tournament_ids": snapshot.tournament_ids,
        "ranking": json.loads(snapshot.json_data)
    }
