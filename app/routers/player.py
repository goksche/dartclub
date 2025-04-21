from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.schemas.player import PlayerCreate, PlayerOut
from app.crud import player as crud
from app.db import get_db
from typing import List
import csv
import io

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


@router.post("/import-csv", tags=["Spieler"])
def import_players_from_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    imported = []
    failed = []

    for row in reader:
        try:
            player_data = PlayerCreate(
                name=row["name"].strip(),
                nickname=row["nickname"].strip(),
                email=row["email"].strip()
            )
            player = crud.create_player(db, player_data)
            imported.append(player.nickname)
        except Exception as e:
            failed.append({"row": row, "error": str(e)})

    return {
        "imported": imported,
        "failed": failed,
        "total": len(imported) + len(failed)
    }
from fastapi.responses import StreamingResponse
import io

@router.get("/export-csv", tags=["Spieler"])
def export_players_to_csv(db: Session = Depends(get_db)):
    players = crud.get_all_players(db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "nickname", "email"])

    for player in players:
        writer.writerow([player.id, player.name, player.nickname, player.email])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=players.csv"}
    )
