# app/schemas.py
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel

from app.models import MatchSide, DraftActionType, UserRole


# ---------- Player ----------

class PlayerCreate(SQLModel):
    name: str

    class Config:
        orm_mode = True


class PlayerRead(SQLModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# ---------- Boss ----------

class BossCreate(SQLModel):
    slug: str
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class BossRead(SQLModel):
    id: int
    slug: str
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


# ---------- Resonator ----------

class ResonatorCreate(SQLModel):
    slug: str
    name: str
    iconUrl: str

    class Config:
        orm_mode = True


class ResonatorRead(SQLModel):
    id: int
    slug: str
    name: str
    iconUrl: str
    isEnabled: bool

    class Config:
        orm_mode = True


# ---------- Match & Draft ----------

class MatchCreate(SQLModel):
    """
    Zum Anlegen eines neuen 1v1-Matches.
    """
    playerLeftId: int
    playerRightId: int
    firstPickSide: MatchSide

class MatchRead(SQLModel):
    id: int
    playerLeftId: int
    playerRightId: int
    firstPickSide: MatchSide
    bossId: Optional[int]
    winnerPlayerId: Optional[int]
    leftTimeSeconds: Optional[int]
    rightTimeSeconds: Optional[int]
    startedAt: Optional[datetime]
    finishedAt: Optional[datetime]

    class Config:
        orm_mode = True


class MatchDraftActionCreate(SQLModel):
    """
    Ein Pick/Ban-Schritt, der zu einem Match hinzugefügt wird.
    """
    stepIndex: int
    actionType: DraftActionType
    actingSide: MatchSide
    resonatorId: int

    class Config:
        orm_mode = True


class MatchDraftActionRead(SQLModel):
    id: int
    stepIndex: int
    actionType: DraftActionType
    actingSide: MatchSide
    resonatorId: int
    createdAt: datetime

    class Config:
        orm_mode = True


class MatchDetail(SQLModel):
    """
    Detailansicht eines Matches inkl. Spieler-Infos und Draft-Aktionen.
    """
    match: MatchRead
    playerLeft: PlayerRead
    playerRight: PlayerRead
    actions: List[MatchDraftActionRead]

    class Config:
        orm_mode = True


# ---------- BossTime / Leaderboard ----------

class BossTimeSubmit(SQLModel):
    """
    Payload, wenn ein Spieler seine Zeit für einen Boss einträgt.
    """
    bossId: int
    playerId: int  # später aus Auth ableiten
    timeSeconds: int

    class Config:
        orm_mode = True


class BossTimeRead(SQLModel):
    id: int
    bossId: int
    playerId: int
    bestTimeSeconds: int
    updatedAt: datetime

    class Config:
        orm_mode = True


class BossLeaderboardEntry(SQLModel):
    playerId: int
    playerName: str
    bestTimeSeconds: int

    class Config:
        orm_mode = True


class BossWithLeaderboard(SQLModel):
    bossId: int
    bossName: str
    top5: List[BossLeaderboardEntry]

    class Config:
        orm_mode = True


class AllBossLeaderboards(SQLModel):
    bosses: List[BossWithLeaderboard]

    class Config:
        orm_mode = True

# ---------- Tournament ----------

class TournamentCreate(SQLModel):
    name: str
    isActive: bool = True

    class Config:
        orm_mode = True


class TournamentRead(SQLModel):
    id: int
    name: str
    isActive: bool

    class Config:
        orm_mode = True


class TournamentWithMatches(SQLModel):
    tournament: TournamentRead
    matches: List[MatchRead]  # MatchRead ist weiter oben definiert

    class Config:
        orm_mode = True


# ---------- User ----------

class UserCreate(SQLModel):
    """
    Wird benutzt, um einen neuen User anzulegen.
    Das Passwort kommt als Klartext rein und wird im Router gehasht.
    """
    username: str
    password: str
    role: UserRole = UserRole.PLAYER
    playerId: Optional[int] = None

    class Config:
        orm_mode = True


class UserRead(SQLModel):
    """
    Öffentliche Darstellung eines Users (ohne Passwort).
    """
    id: int
    username: str
    role: UserRole
    playerId: Optional[int] = None

    class Config:
        orm_mode = True
