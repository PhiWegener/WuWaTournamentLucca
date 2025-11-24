from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import getSession
from app.models import Player
from app.schemas import PlayerCreate, PlayerRead

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/", response_model=PlayerRead)
def createPlayer(data: PlayerCreate, session: Session = Depends(getSession)):
    player = Player(name=data.name)
    session.add(player)
    session.commit()
    session.refresh(player)
    return PlayerRead.from_orm(player)


@router.get("/", response_model=list[PlayerRead])
def listPlayers(session: Session = Depends(getSession)):
    players = session.exec(select(Player)).all()
    return [PlayerRead.from_orm(p) for p in players]


@router.get("/{playerId}", response_model=PlayerRead)
def getPlayer(playerId: int, session: Session = Depends(getSession)):
    player = session.get(Player, playerId)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerRead.from_orm(player)
