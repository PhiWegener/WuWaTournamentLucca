from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import getSession
from app.models import Boss
from app.schemas import BossCreate, BossRead

router = APIRouter(prefix="/bosses", tags=["bosses"])


@router.post("/", response_model=BossRead)
def createBoss(data: BossCreate, session: Session = Depends(getSession)):
    existing = session.exec(select(Boss).where(Boss.slug == data.slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    boss = Boss(slug=data.slug, name=data.name, description=data.description)
    session.add(boss)
    session.commit()
    session.refresh(boss)
    return BossRead.from_orm(boss)


@router.get("/", response_model=list[BossRead])
def listBosses(session: Session = Depends(getSession)):
    bosses = session.exec(select(Boss)).all()
    return [BossRead.from_orm(b) for b in bosses]


@router.get("/{bossId}", response_model=BossRead)
def getBoss(bossId: int, session: Session = Depends(getSession)):
    boss = session.get(Boss, bossId)
    if not boss:
        raise HTTPException(status_code=404, detail="Boss not found")
    return BossRead.from_orm(boss)
