from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.player import Player
from app.models.tournament import Tournament
from app.models.match import Match
from app.schemas.tournament import TournamentCreate
from app.crud.player import create_player
from app.crud.tournament import create_tournament, add_player_to_tournament
from app.services.ko_logic import generate_ko_matches
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



def run():
    db: Session = SessionLocal()

    names = ["A_Mario", "B_Tina", "A_Lisa", "B_Chris", "A_Leon", "B_Sara", "A_Felix", "B_Anna"]
    players = []
    for name in names:
        p = create_player(db, name=name, nickname=name, email=f"{name.lower()}@test.de")
        players.append(p)

    tournament = create_tournament(db, TournamentCreate(
        name="KO Test Cup",
        type="wertung",
        mode="ko",
        date="2025-05-10",
        is_ranked=True,
        best_of=3,
        seeded_players=[]
    ))

    for p in players:
        add_player_to_tournament(db, tournament, p)

    generate_ko_matches(db, tournament, players)

    matches = db.query(Match).filter(Match.tournament_id == tournament.id).all()
    for m in matches:
        if m.player2_id is not None:
            l1 = random.randint(0, 2)
            l2 = 2 - l1
            m.legs_player1 = l1
            m.legs_player2 = l2
            db.commit()

    print(f"✅ KO-Testturnier erstellt: Turnier-ID = {tournament.id}")


if __name__ == "__main__":
    run()
