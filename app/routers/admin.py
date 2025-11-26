from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.passwords import verifyPassword
from app.sessions import loginUser, requireAdmin

from app.database import getSession
from app.models import User, UserRole, Tournament, Boss, Resonator
from app.schemas import UserCreate


router = APIRouter(prefix="/admin", tags=["admin"])

templates = Jinja2Templates(directory="app/templates")


# ---------- LOGIN ----------
@router.get("/login")
def loginForm(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.post("/login")
def loginSubmit(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(getSession)
):
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user or not verifyPassword(password, user.passwordHash):
        return templates.TemplateResponse("admin_login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    loginUser(response, user.id)
    return Response(status_code=302, headers={"Location": "/admin"})


# ---------- DASHBOARD ----------
@router.get("/", dependencies=[Depends(requireAdmin)])
def adminHome(request: Request):
    return templates.TemplateResponse("admin_dashboard.html",
        {"request": request}
    )


# ---------- TOURNAMENTS ----------
@router.get("/tournaments", dependencies=[Depends(requireAdmin)])
def adminTournaments(
    request: Request,
    session: Session = Depends(getSession)
):
    tournaments = session.exec(select(Tournament)).all()
    return templates.TemplateResponse("admin_tournaments.html",
        {"request": request, "tournaments": tournaments}
    )


@router.post("/tournaments", dependencies=[Depends(requireAdmin)])
def createTournament(
    request: Request,
    name: str = Form(...),
    session: Session = Depends(getSession)
):
    t = Tournament(name=name)
    session.add(t)
    session.commit()
    return Response(status_code=302, headers={"Location": "/admin/tournaments"})


# ---------- BOSSES ----------
@router.get("/bosses", dependencies=[Depends(requireAdmin)])
def adminBosses(request: Request, session: Session = Depends(getSession)):
    bosses = session.exec(select(Boss)).all()
    return templates.TemplateResponse("admin_bosses.html",
        {"request": request, "bosses": bosses}
    )


@router.post("/bosses", dependencies=[Depends(requireAdmin)])
def createBoss(
    name: str = Form(...),
    slug: str = Form(...),
    session: Session = Depends(getSession)
):
    b = Boss(name=name, slug=slug)
    session.add(b)
    session.commit()
    return Response(status_code=302, headers={"Location": "/admin/bosses"})


# ---------- RESONATORS ----------
@router.get("/resonators", dependencies=[Depends(requireAdmin)])
def adminResonators(request: Request, session: Session = Depends(getSession)):
    resonators = session.exec(select(Resonator)).all()
    return templates.TemplateResponse("admin_resonators.html",
        {"request": request, "resonators": resonators}
    )


@router.post("/resonators", dependencies=[Depends(requireAdmin)])
def createResonator(
    slug: str = Form(...),
    name: str = Form(...),
    iconUrl: str = Form(...),
    session: Session = Depends(getSession)
):
    r = Resonator(slug=slug, name=name, iconUrl=iconUrl)
    session.add(r)
    session.commit()
    return Response(status_code=302, headers={"Location": "/admin/resonators"})


# ---------- USERS ----------
@router.get("/users", dependencies=[Depends(requireAdmin)])
def adminUsers(request: Request, session: Session = Depends(getSession)):
    users = session.exec(select(User)).all()
    return templates.TemplateResponse("admin_users.html",
        {"request": request, "users": users}
    )


@router.post("/users", dependencies=[Depends(requireAdmin)])
def createUserAdmin(
    username: str = Form(...),
    password: str = Form(...),
    role: UserRole = Form(UserRole.PLAYER),
    playerId: int = Form(None),
    session: Session = Depends(getSession)
):
    from app.security import hashPassword
    u = User(
        username=username,
        passwordHash=hashPassword(password),
        role=role,
        playerId=playerId,
    )
    session.add(u)
    session.commit()
    return Response(status_code=302, headers={"Location": "/admin/users"})
