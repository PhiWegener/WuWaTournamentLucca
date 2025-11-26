# app/sessions.py
from fastapi import Request, HTTPException, Response, Depends
from sqlmodel import Session

from app.models import User, UserRole
from app.database import getSession
import uuid

sessions = {}  # { session_id: user_id }


def loginUser(response: Response, userId: int):
    sessionId = str(uuid.uuid4())
    sessions[sessionId] = userId

    response.set_cookie(
        key="session_id",
        value=sessionId,
        httponly=True,
        max_age=3600 * 24,
        samesite="lax",
    )


def getCurrentUser(
    request: Request,
    session: Session = Depends(getSession),
) -> User | None:
    sessionId = request.cookies.get("session_id")
    if not sessionId:
        return None
    if sessionId not in sessions:
        return None

    userId = sessions[sessionId]
    return session.get(User, userId)


def requireAdmin(
    request: Request,
    session: Session = Depends(getSession),
) -> User:
    user = getCurrentUser(request, session)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not an admin")
    return user
