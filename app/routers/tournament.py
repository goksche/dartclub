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
