from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import getSession
from app.models import Match, Player, MatchDraftAction
from app.schemas import (
    MatchCreate,
    MatchRead,
    MatchDetail,
    MatchDraftActionCreate,
    MatchDraftActionRead,
    PlayerRead,
)

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/", response_model=MatchRead)
def createMatch(data: MatchCreate, session: Session = Depends(getSession)):
    playerLeft = session.get(Player, data.playerLeftId)
    playerRight = session.get(Player, data.playerRightId)

    if not playerLeft or not playerRight:
        raise HTTPException(status_code=400, detail="Player not found")

    match = Match(
        playerLeftId=playerLeft.id,
        playerRightId=playerRight.id,
        firstPickSide=data.firstPickSide,
        bossId=data.bossId,
    )
    session.add(match)
    session.commit()
    session.refresh(match)
    return MatchRead.from_orm(match)


@router.get("/{matchId}", response_model=MatchDetail)
def getMatchDetail(matchId: int, session: Session = Depends(getSession)):
    match = session.get(Match, matchId)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    actions = session.exec(
        select(MatchDraftAction)
        .where(MatchDraftAction.matchId == matchId)
        .order_by(MatchDraftAction.stepIndex)
    ).all()

    matchRead = MatchRead.from_orm(match)
    playerLeftRead = PlayerRead.from_orm(match.playerLeft)
    playerRightRead = PlayerRead.from_orm(match.playerRight)
    actionsRead = [MatchDraftActionRead.from_orm(a) for a in actions]

    return MatchDetail(
        match=matchRead,
        playerLeft=playerLeftRead,
        playerRight=playerRightRead,
        actions=actionsRead,
    )


@router.post("/{matchId}/actions", response_model=MatchDraftActionRead)
def addDraftAction(
    matchId: int,
    data: MatchDraftActionCreate,
    session: Session = Depends(getSession),
):
    match = session.get(Match, matchId)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    action = MatchDraftAction(
        matchId=matchId,
        stepIndex=data.stepIndex,
        actionType=data.actionType,
        actingSide=data.actingSide,
        resonatorId=data.resonatorId,
    )
    session.add(action)
    session.commit()
    session.refresh(action)
    return MatchDraftActionRead.from_orm(action)


@router.post("/{matchId}/winner/{playerId}", response_model=MatchRead)
def setMatchWinner(
    matchId: int,
    playerId: int,
    session: Session = Depends(getSession),
):
    match = session.get(Match, matchId)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    player = session.get(Player, playerId)
    if not player:
        raise HTTPException(status_code=400, detail="Player not found")

    if playerId not in (match.playerLeftId, match.playerRightId):
        raise HTTPException(status_code=400, detail="Player is not part of this match")

    match.winnerPlayerId = playerId
    session.add(match)
    session.commit()
    session.refresh(match)
    return MatchRead.from_orm(match)
