from sqlalchemy.orm import Session
from app.models.match import Match
from app.models.player import Player
from app.models.tournament import Tournament
from app.crud import match as match_crud
from collections import defaultdict

def generate_round_robin_matches(db: Session, tournament: Tournament, players: list[Player]):
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            match_crud.create_match(db, tournament.id, players[i].id, players[j].id, tournament.best_of)

def calculate_ranking(db: Session, tournament_id: int, players: list[Player]):
    matches = match_crud.get_matches_by_tournament(db, tournament_id)
    score = defaultdict(int)
    direct = defaultdict(lambda: defaultdict(int))

    for match in matches:
        if match.legs_player1 is None or match.legs_player2 is None:
            continue
        diff = match.legs_player1 - match.legs_player2
        score[match.player1_id] += diff
        score[match.player2_id] -= diff
        # Direktvergleich für TieBreaker
        if diff > 0:
            direct[match.player1_id][match.player2_id] += 1
        elif diff < 0:
            direct[match.player2_id][match.player1_id] += 1

    # Tiebreak nach Direktvergleich bei Gleichstand
    def rank_key(pid):
        return (score[pid], sum(direct[pid].values()))

    ranking = sorted(players, key=lambda p: rank_key(p.id), reverse=True)
    return [{"player_id": p.id, "nickname": p.nickname, "leg_diff": score[p.id]} for p in ranking]
