# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.database import getSession
from app.models import User, UserRole

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def getCurrentUser(
    token: str = Depends(oauth2Scheme),
    session: Session = Depends(getSession),
) -> User:
    """
    Hier würdest du den Token decodieren, User-Id rausziehen und User laden.
    Für den Anfang kannst du das auch fake-mäßig machen, bis Auth steht.
    """
    # TODO: JWT decodieren und User aus DB laden
    # Platzhalter:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Auth not implemented yet",
    )


def requireRole(requiredRoles: list[UserRole]):
    def dependency(user: User = Depends(getCurrentUser)) -> User:
        if user.role not in requiredRoles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return user
    return dependency
