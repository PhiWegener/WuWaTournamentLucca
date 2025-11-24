# app/models.py
from typing import Optional, List
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship


class MatchSide(str, Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class DraftActionType(str, Enum):
    PICK = "PICK"
    BAN = "BAN"

class Tournament(SQLModel, table=True):
    """
    Ein Turnier/Event mit mehreren Matches
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    isActive: bool = Field(default=True)

    matches: List["Match"] = Relationship(back_populates="tournament")


class Resonator(SQLModel, table=True):
    """
    Repräsentiert einen spielbaren Resonator (Champ).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)   # z.B. "verina"
    name: str
    iconUrl: str
    isEnabled: bool = Field(default=True)


class Player(SQLModel, table=True):
    """
    Repräsentiert einen Spieler.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    matchesLeft: List["Match"] = Relationship(back_populates="playerLeft", sa_relationship_kwargs={"foreign_keys": "[Match.playerLeftId]"})
    matchesRight: List["Match"] = Relationship(back_populates="playerRight", sa_relationship_kwargs={"foreign_keys": "[Match.playerRightId]"})


class Match(SQLModel, table=True):
    """
    Ein Match zwischen zwei Spielern.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    tournamentId: Optional[int] = Field(default=None, foreign_key="tournament.id")
    tournament: Optional[Tournament] = Relationship(back_populates="matches")

    playerLeftId: int = Field(foreign_key="player.id")
    playerRightId: int = Field(foreign_key="player.id")

    playerLeft: Player = Relationship(back_populates="matchesLeft", sa_relationship_kwargs={"foreign_keys": "[Match.playerLeftId]"})
    playerRight: Player = Relationship(back_populates="matchesRight", sa_relationship_kwargs={"foreign_keys": "[Match.playerRightId]"})

    firstPickSide: MatchSide
    winnerSide: Optional[MatchSide] = None

    bestTimeSeconds: Optional[int] = None
    roundName: Optional[str] = None

    startedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None

    # Picks/Bans-Protokoll
    actions: list["MatchDraftAction"] = Relationship(back_populates="match")


class MatchDraftAction(SQLModel, table=True):
    """
    Ein einzelner Pick- oder Ban-Schritt in einem Match.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    matchId: int = Field(foreign_key="match.id", index=True)
    match: Match = Relationship(back_populates="actions")

    stepIndex: int = Field(index=True)
    actionType: DraftActionType
    actingSide: MatchSide

    resonatorId: int = Field(foreign_key="resonator.id")
    resonator: Resonator = Relationship()

    createdAt: datetime = Field(default_factory=datetime.utcnow)


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    COMMENTATOR = "COMMENTATOR"
    PLAYER = "PLAYER"

class User(SQLModel, table=True):
    """
    App-User mit Login,
    Ein User kann Optional einem Player zugeordnet sein.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    passwordHash: str

    role: UserRole = Field(default=UserRole.PLAYER)
    
    playerId: Optional[int] = Field(default=None, foreign_key="player.id")
    player: Optional[Player] = Relationship()

class Boss(SQLModel, table=True):
    """
    Boss, gegen den die Zeitrennen laufen.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str
    description: Optional[str] = None

class BossTime(SQLModel, table=True):
    """
    Bestzeit eines Spielers für einen bestimmten Boss.
    Einzigartig pro Spieler + Boss
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    
    playerId: int = Field(foreign_key="player.id", index=True)
    player: Player = Relationship()

    bossId: int = Field(foreign_key="boss.id", index=True)
    boss: Boss = Relationship()

    bestTimeSeconds: int = Field(index=True)
    updatetAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # Bei SQLModel kannst du einen Unique-Index auch so ergänzen:
        # __table_args__ = (UniqueConstraint("playerId", "bossId"),)
        pass