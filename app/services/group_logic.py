import random
from sqlalchemy.orm import Session
from collections import defaultdict
from typing import Dict
from app.models.tournament import Tournament
from app.models.player import Player
from app.models.match import Match
from app.crud import match as match_crud
from app.services.ko_logic import generate_ko_matches


def generate_grouped_round_robin_matches(
    db: Session,
    tournament: Tournament,
    players: list[Player],
    seeded_players: list[int]
):
    group_count = 2
    groups: Dict[str, list[int]] = {"A": [], "B": []}
    player_ids = [p.id for p in players]

    if len(seeded_players) >= 1:
        groups["A"].append(seeded_players[0])
        player_ids.remove(seeded_players[0])
    if len(seeded_players) >= 2:
        groups["B"].append(seeded_players[1])
        player_ids.remove(seeded_players[1])

    random.shuffle(player_ids)
    for idx, pid in enumerate(player_ids):
        if idx % 2 == 0:
            groups["A"].append(pid)
        else:
            groups["B"].append(pid)

    for group_name, pids in groups.items():
        for i in range(len(pids)):
            for j in range(i + 1, len(pids)):
                match_crud.create_match(
                    db=db,
                    tournament_id=tournament.id,
                    p1_id=pids[i],
                    p2_id=pids[j],
                    best_of=tournament.best_of
                )
    return groups


def calculate_ranking(db: Session, tournament_id: int, players: list[Player]):
    matches = db.query(Match).filter(Match.tournament_id == tournament_id).all()
    stats = {
        player.id: {
            "id": player.id,
            "nickname": player.nickname,
            "group": player.nickname.split("_")[0] if "_" in player.nickname else None,
            "points": 0,
            "leg_diff": 0,
            "wins": 0,
            "losses": 0
        } for player in players
    }
    direct_duels = {}

    for match in matches:
        if match.legs_player1 is None or match.legs_player2 is None:
            continue

        p1, p2 = match.player1_id, match.player2_id
        l1, l2 = match.legs_player1, match.legs_player2

        stats[p1]["leg_diff"] += l1 - l2
        stats[p2]["leg_diff"] += l2 - l1

        if l1 > l2:
            stats[p1]["points"] += 2
            stats[p1]["wins"] += 1
            stats[p2]["losses"] += 1
            direct_duels[f"{p1}_{p2}"] = p1
        else:
            stats[p2]["points"] += 2
            stats[p2]["wins"] += 1
            stats[p1]["losses"] += 1
            direct_duels[f"{p1}_{p2}"] = p2

    def sort_key(item):
        s = item[1]
        return (-s["points"], -s["leg_diff"])

    sorted_stats = sorted(stats.items(), key=sort_key)

    result = []
    i = 0
    pos = 1
    while i < len(sorted_stats):
        same_group = [sorted_stats[i]]
        while (
            i + 1 < len(sorted_stats)
            and sorted_stats[i][1]["points"] == sorted_stats[i + 1][1]["points"]
            and sorted_stats[i][1]["leg_diff"] == sorted_stats[i + 1][1]["leg_diff"]
        ):
            same_group.append(sorted_stats[i + 1])
            i += 1

        if len(same_group) == 2:
            p1, p2 = same_group[0][0], same_group[1][0]
            duel_key = f"{p1}_{p2}" if f"{p1}_{p2}" in direct_duels else f"{p2}_{p1}"
            winner = direct_duels.get(duel_key)
            if winner == p2:
                same_group = [same_group[1], same_group[0]]

        for s in same_group:
            s_data = s[1]
            s_data["position"] = pos
            result.append(s_data)
            pos += 1

        i += 1

    return result


def start_defined_ko_bracket(db: Session, tournament: Tournament, players: list[Player]):
    groups = {"A": [], "B": []}
    for player in players:
        if player.nickname.startswith("A_"):
            groups["A"].append(player)
        elif player.nickname.startswith("B_"):
            groups["B"].append(player)

    if not groups["A"] or not groups["B"]:
        raise Exception("Gruppenzugehörigkeit fehlt in Nickname")

    rankings = {
        "A": calculate_ranking(db, tournament.id, groups["A"]),
        "B": calculate_ranking(db, tournament.id, groups["B"]),
    }

    def pid(rank_list, idx):
        return rank_list[idx]["id"]

    matchups = [
        (pid(rankings["A"], 0), pid(rankings["B"], 3)),  # A1 vs B4
        (pid(rankings["B"], 0), pid(rankings["A"], 3)),  # B1 vs A4
        (pid(rankings["A"], 1), pid(rankings["B"], 2)),  # A2 vs B3
        (pid(rankings["B"], 1), pid(rankings["A"], 2)),  # B2 vs A3
    ]

    for p1, p2 in matchups:
        match_crud.create_ko_match(
            db=db,
            tournament_id=tournament.id,
            p1_id=p1,
            p2_id=p2,
            best_of=tournament.best_of,
            round=1
        )

    return {"status": "Viertelfinale generiert", "matches": matchups}
