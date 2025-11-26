# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import getSession
from app.models import User, Player, UserRole
from app.schemas import UserCreate, UserRead
from app.passwords import hashPassword

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def createUser(data: UserCreate, session: Session = Depends(getSession)):
    """
    Legt einen neuen User an, hash das Passwort
    und verknüpft optional mit einem Player.
    """
    existing = session.exec(
        select(User).where(User.username == data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    player = None
    if data.playerId is not None:
        player = session.get(Player, data.playerId)
        if not player:
            raise HTTPException(status_code=400, detail="Player not found")

    passwordHash=hashPassword(data.password)

    user = User(
        username=data.username,
        passwordHash=passwordHash,
        role=data.role,
        playerId=data.playerId,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return UserRead.from_orm(user)


@router.get("/", response_model=list[UserRead])
def listUsers(session: Session = Depends(getSession)):
    """
    Gibt alle User (ohne Passwort) zurück.
    """
    users = session.exec(select(User)).all()
    return [UserRead.from_orm(u) for u in users]


@router.get("/{userId}", response_model=UserRead)
def getUser(userId: int, session: Session = Depends(getSession)):
    """
    Gibt einen einzelnen User zurück.
    """
    user = session.get(User, userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(user)
