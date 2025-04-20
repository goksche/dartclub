from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.player import PlayerCreate, PlayerOut
from app.crud import player as crud
from app.db import get_db
from typing import List

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "🧠 Spieler-Modul bereit"}

@router.post("/", response_model=PlayerOut)
def create(player: PlayerCreate, db: Session = Depends(get_db)):
    return crud.create_player(db, player)

@router.get("/", response_model=List[PlayerOut])
def list_all(db: Session = Depends(get_db)):
    return crud.get_all_players(db)

@router.get("/{player_id}", response_model=PlayerOut)
def get_by_id(player_id: int, db: Session = Depends(get_db)):
    player = crud.get_player_by_id(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden")
    return player

@router.get("/nickname/{nickname}", response_model=PlayerOut)
def get_by_nickname(nickname: str, db: Session = Depends(get_db)):
    player = crud.get_player_by_nickname(db, nickname)
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden")
    return player

@router.put("/{player_id}", response_model=PlayerOut)
def update(player_id: int, data: PlayerCreate, db: Session = Depends(get_db)):
    return crud.update_player(db, player_id, data)

@router.delete("/{player_id}")
def delete(player_id: int, db: Session = Depends(get_db)):
    crud.delete_player(db, player_id)
    return {"detail": "Spieler gelöscht"}
