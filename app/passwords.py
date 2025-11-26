# app/passwords.py
from passlib.context import CryptContext

# Wir verwenden bcrypt_sha256 statt plain bcrypt:
# - schützt besser lange/komplexe Passwörter
# - umgeht das 72-Byte-Limit-Drama des Backends
passwordContext = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto",
)


def hashPassword(plainPassword: str) -> str:
    """
    Erzeugt einen Hash für ein Klartextpasswort.
    Das Passwort wird intern zuerst mit SHA-256 gehasht und dann via bcrypt verarbeitet.
    """
    return passwordContext.hash(plainPassword)


def verifyPassword(plainPassword: str, passwordHash: str) -> bool:
    """
    Prüft, ob das Klartextpasswort zum gespeicherten Hash passt.
    """
    return passwordContext.verify(plainPassword, passwordHash)
