# app/security.py
from passlib.context import CryptContext

passwordContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashPassword(plainPassword: str) -> str:
    """
    Erzeugt einen sicheren Hash für ein Klartextpasswort.
    """
    return passwordContext.hash(plainPassword)


def verifyPassword(plainPassword: str, passwordHash: str) -> bool:
    """
    Prüft, ob das Klartextpasswort zum gespeicherten Hash passt.
    """
    return passwordContext.verify(plainPassword, passwordHash)
