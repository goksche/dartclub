from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.match import MatchReport, MatchOut
from app.crud import match as crud
from typing import List

router = APIRouter()

@router.post("/{match_id}/report", response_model=MatchOut)
def report_result(match_id: int, result: MatchReport, db: Session = Depends(get_db)):
    return crud.report_match_result(db, match_id, result)

@router.get("/tournament/{tournament_id}/matches", response_model=List[MatchOut])
def get_matches(tournament_id: int, db: Session = Depends(get_db)):
    return crud.get_matches_by_tournament(db, tournament_id)

from app.services.ko_logic import advance_winner


@router.post("/{match_id}/report", response_model=MatchOut)
def report_result(match_id: int, result: MatchReport, db: Session = Depends(get_db)):
    match = crud.report_match_result(db, match_id, result)

    # KO-Modus: automatisch Sieger weiterbringen
    advance_winner(db, match)

    return match
