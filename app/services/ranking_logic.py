from app.models.tournament import Tournament
from app.models.match import Match
from app.models.player import Player
from sqlalchemy.orm import Session

def calculate_overall_ranking(db: Session, tournaments: list[Tournament]):
    player_points = defaultdict(lambda: {
        "player_id": None,
        "nickname": "",
        "total_points": 0,
        "participations": 0,
        "placements": []
    })

    for tournament in tournaments:
        matches = db.query(Match).filter(Match.tournament_id == tournament.id).all()
        players = tournament.players
        ranking = _calculate_single_tournament_ranking(matches, players)

        for place, player_id in enumerate(ranking, start=1):
            points = _get_points_for_place(place)
            p = player_points[player_id]
            p["player_id"] = player_id
            p["nickname"] = next((pl.nickname for pl in players if pl.id == player_id), f"#{player_id}")
            p["total_points"] += points
            p["participations"] += 1
            p["placements"].append({"tournament_id": tournament.id, "place": place, "points": points})

    ranked = sorted(player_points.values(), key=lambda x: -x["total_points"])

    for i, p in enumerate(ranked, start=1):
        p["position"] = i

    return ranked


def _calculate_single_tournament_ranking(matches: list[Match], players: list[Player]):
    stats = {p.id: {"wins": 0, "leg_diff": 0} for p in players}

    for match in matches:
        if match.legs_player1 is None or match.legs_player2 is None:
            continue

        p1 = match.player1_id
        p2 = match.player2_id

        if match.legs_player1 > match.legs_player2:
            stats[p1]["wins"] += 1
        else:
            stats[p2]["wins"] += 1

        stats[p1]["leg_diff"] += match.legs_player1 - match.legs_player2
        stats[p2]["leg_diff"] += match.legs_player2 - match.legs_player1

    sorted_players = sorted(stats.items(), key=lambda item: (-item[1]["wins"], -item[1]["leg_diff"]))
    return [pid for pid, _ in sorted_players]


def _get_points_for_place(place: int) -> int:
    if place == 1:
        return 30
    elif place == 2:
        return 24
    elif place == 3:
        return 18
    elif place == 4:
        return 15
    elif place >= 5:
        return 5
    return 0
