from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import getSession
from app.models import Resonator
from app.schemas import ResonatorCreate, ResonatorRead

router = APIRouter(prefix="/resonators", tags=["resonators"])


@router.post("/", response_model=ResonatorRead)
def createResonator(data: ResonatorCreate, session: Session = Depends(getSession)):
    existing = session.exec(select(Resonator).where(Resonator.slug == data.slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    resonator = Resonator(
        slug=data.slug,
        name=data.name,
        iconUrl=data.iconUrl,
    )
    session.add(resonator)
    session.commit()
    session.refresh(resonator)
    return ResonatorRead.from_orm(resonator)


@router.get("/", response_model=list[ResonatorRead])
def listResonators(session: Session = Depends(getSession)):
    resonators = session.exec(select(Resonator)).all()
    return [ResonatorRead.from_orm(r) for r in resonators]
