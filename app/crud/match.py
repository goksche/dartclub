from sqlalchemy.orm import Session
from app.models.match import Match
from app.schemas.match import MatchReport

def create_match(db: Session, tournament_id: int, p1_id: int, p2_id: int, best_of: int):
    match = Match(
        tournament_id=tournament_id,
        player1_id=p1_id,
        player2_id=p2_id,
        best_of=best_of
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

def report_match_result(db: Session, match_id: int, report: MatchReport):
    match = db.query(Match).filter(Match.id == match_id).first()
    match.legs_player1 = report.legs_player1
    match.legs_player2 = report.legs_player2
    db.commit()
    db.refresh(match)
    return match

def get_matches_by_tournament(db: Session, tournament_id: int):
    return db.query(Match).filter(Match.tournament_id == tournament_id).all()
