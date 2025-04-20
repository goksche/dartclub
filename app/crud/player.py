from sqlalchemy.orm import Session
from app.models.player import Player
from app.schemas.player import PlayerCreate

def create_player(db: Session, player: PlayerCreate):
    db_player = Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def get_player_by_id(db: Session, player_id: int):
    return db.query(Player).filter(Player.id == player_id).first()

def get_player_by_nickname(db: Session, nickname: str):
    return db.query(Player).filter(Player.nickname == nickname).first()

def get_all_players(db: Session):
    return db.query(Player).all()

def update_player(db: Session, player_id: int, player_data: PlayerCreate):
    player = get_player_by_id(db, player_id)
    if player:
        for field, value in player_data.dict().items():
            setattr(player, field, value)
        db.commit()
        db.refresh(player)
    return player

def delete_player(db: Session, player_id: int):
    player = get_player_by_id(db, player_id)
    if player:
        db.delete(player)
        db.commit()
    return player
