from sqlalchemy.orm import Session
from app.models.match import Match
from app.crud import match as crud

def advance_winner(db: Session, match: Match):
    if match.legs_player1 is None or match.legs_player2 is None:
        return

    winner_id = match.player1_id if match.legs_player1 > match.legs_player2 else match.player2_id
    match.round = match.round or 1
    next_round = match.round + 1

    current_round_matches = db.query(Match).filter(
        Match.tournament_id == match.tournament_id,
        Match.round == match.round
    ).all()

    if any(m.legs_player1 is None or m.legs_player2 is None for m in current_round_matches):
        return

    winners = []
    for m in current_round_matches:
        if m.legs_player1 > m.legs_player2:
            winners.append(m.player1_id)
        else:
            winners.append(m.player2_id)

    for i in range(0, len(winners), 2):
        p1 = winners[i]
        p2 = winners[i + 1] if i + 1 < len(winners) else None
        crud.create_ko_match(db, match.tournament_id, p1, p2, match.best_of, next_round)
