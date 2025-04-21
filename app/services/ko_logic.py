from sqlalchemy.orm import Session
from app.models.player import Player
from app.models.tournament import Tournament
from app.models.match import Match
from app.crud import match as crud
import math
import random


def generate_ko_matches(db: Session, tournament: Tournament, players: list[Player]):
    players_ids = [p.id for p in players]
    random.shuffle(players_ids)

    total_players = len(players_ids)
    next_power_of_two = 2 ** math.ceil(math.log2(total_players))
    byes = next_power_of_two - total_players

    matches = []

    round_number = 1  # Start mit Runde 1 (z. B. Achtel)

    index = 0
    while index < total_players - 1:
        p1 = players_ids[index]
        p2 = players_ids[index + 1]
        match = crud.create_ko_match(db, tournament.id, p1, p2, tournament.best_of, round_number)
        matches.append(match)
        index += 2

    # Freilose: Spieler automatisch in nächste Runde setzen
    if byes:
        for i in range(byes):
            player_id = players_ids[-(i + 1)]
            match = crud.create_ko_match(db, tournament.id, player_id, None, tournament.best_of, round_number)
            matches.append(match)

    return matches


def advance_winner(db: Session, match: Match):
    if match.legs_player1 is None or match.legs_player2 is None:
        return

    winner_id = match.player1_id if match.legs_player1 > match.legs_player2 else match.player2_id
    match.round = match.round or 1

    next_round = match.round + 1

    # 🔁 Prüfe, ob alle Matches in dieser Runde abgeschlossen sind
    current_round_matches = db.query(Match).filter(
        Match.tournament_id == match.tournament_id,
        Match.round == match.round
    ).all()

    if any(m.legs_player1 is None or m.legs_player2 is None for m in current_round_matches):
        return  # noch nicht alle Spiele fertig

    # 🧠 Gewinner aller Matches dieser Runde sammeln
    winners = []
    for m in current_round_matches:
        if m.legs_player1 > m.legs_player2:
            winners.append(m.player1_id)
        else:
            winners.append(m.player2_id)

    # 🔁 KO-Matches für nächste Runde erzeugen
    for i in range(0, len(winners), 2):
        p1 = winners[i]
        p2 = winners[i + 1] if i + 1 < len(winners) else None
        crud.create_ko_match(db, match.tournament_id, p1, p2, match.best_of, next_round)
