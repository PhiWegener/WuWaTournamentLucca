from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import getSession
from app.models import BossTime, Player, Boss
from app.schemas import (
    BossTimeSubmit,
    BossTimeRead,
    BossLeaderboardEntry,
    BossWithLeaderboard,
    AllBossLeaderboards,
)

router = APIRouter(prefix="/boss-times", tags=["boss-times"])


@router.post("/submit", response_model=BossTimeRead)
def submitBossTime(
    data: BossTimeSubmit,
    session: Session = Depends(getSession),
):
    player = session.get(Player, data.playerId)
    if not player:
        raise HTTPException(status_code=400, detail="Player not found")

    boss = session.get(Boss, data.bossId)
    if not boss:
        raise HTTPException(status_code=400, detail="Boss not found")

    if data.timeSeconds <= 0:
        raise HTTPException(status_code=400, detail="Time must be > 0")

    existing = session.exec(
        select(BossTime)
        .where(BossTime.playerId == data.playerId)
        .where(BossTime.bossId == data.bossId)
    ).first()

    if existing is None:
        bossTime = BossTime(
            playerId=data.playerId,
            bossId=data.bossId,
            bestTimeSeconds=data.timeSeconds,
        )
        session.add(bossTime)
        session.commit()
        session.refresh(bossTime)
        return BossTimeRead.from_orm(bossTime)
    else:
        # nur verbessern, wenn neue Zeit besser
        if data.timeSeconds < existing.bestTimeSeconds:
            existing.bestTimeSeconds = data.timeSeconds
            session.add(existing)
            session.commit()
            session.refresh(existing)
        return BossTimeRead.from_orm(existing)


@router.get("/boss/{bossId}/top5", response_model=list[BossLeaderboardEntry])
def getTop5ForBoss(bossId: int, session: Session = Depends(getSession)):
    boss = session.get(Boss, bossId)
    if not boss:
        raise HTTPException(status_code=404, detail="Boss not found")

    records = session.exec(
        select(BossTime)
        .where(BossTime.bossId == bossId)
        .order_by(BossTime.bestTimeSeconds.asc())
        .limit(5)
    ).all()

    return [
        BossLeaderboardEntry(
            playerId=bt.playerId,
            playerName=bt.player.name,
            bestTimeSeconds=bt.bestTimeSeconds,
        )
        for bt in records
    ]


@router.get("/leaderboards", response_model=AllBossLeaderboards)
def getAllLeaderboards(session: Session = Depends(getSession)):
    bosses = session.exec(select(Boss)).all()

    bossEntries: list[BossWithLeaderboard] = []

    for boss in bosses:
        records = session.exec(
            select(BossTime)
            .where(BossTime.bossId == boss.id)
            .order_by(BossTime.bestTimeSeconds.asc())
            .limit(5)
        ).all()

        top5 = [
            BossLeaderboardEntry(
                playerId=bt.playerId,
                playerName=bt.player.name,
                bestTimeSeconds=bt.bestTimeSeconds,
            )
            for bt in records
        ]

        bossEntries.append(
            BossWithLeaderboard(
                bossId=boss.id,
                bossName=boss.name,
                top5=top5,
            )
        )

    return AllBossLeaderboards(bosses=bossEntries)
