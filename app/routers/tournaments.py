from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import getSession
from app.models import Tournament, Match
from app.schemas import (
    TournamentCreate,
    TournamentRead,
    TournamentWithMatches,
    MatchRead,
)

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.post("/", response_model=TournamentRead)
def createTournament(
    data: TournamentCreate,
    session: Session = Depends(getSession),
):
    tournament = Tournament(
        name=data.name,
        isActive=data.isActive,
    )
    session.add(tournament)
    session.commit()
    session.refresh(tournament)
    return TournamentRead.from_orm(tournament)


@router.get("/", response_model=list[TournamentRead])
def listTournaments(session: Session = Depends(getSession)):
    tournaments = session.exec(select(Tournament)).all()
    return [TournamentRead.from_orm(t) for t in tournaments]


@router.get("/{tournamentId}", response_model=TournamentRead)
def getTournament(tournamentId: int, session: Session = Depends(getSession)):
    tournament = session.get(Tournament, tournamentId)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return TournamentRead.from_orm(tournament)


@router.get("/{tournamentId}/matches", response_model=TournamentWithMatches)
def getTournamentWithMatches(
    tournamentId: int,
    session: Session = Depends(getSession),
):
    tournament = session.get(Tournament, tournamentId)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    matches = session.exec(
        select(Match).where(Match.tournamentId == tournamentId)
    ).all()

    matchesRead = [MatchRead.from_orm(m) for m in matches]

    return TournamentWithMatches(
        tournament=TournamentRead.from_orm(tournament),
        matches=matchesRead,
    )
