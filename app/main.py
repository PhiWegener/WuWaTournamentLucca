from fastapi import FastAPI

from app.database import initDatabase
from app.routers import players, bosses, resonators, matches, bosstimes, tournaments, users


def createApp() -> FastAPI:
    app = FastAPI(title="WuWa Tournament API")

    app.include_router(players.router)
    app.include_router(bosses.router)
    app.include_router(resonators.router)
    app.include_router(matches.router)
    app.include_router(bosstimes.router)
    app.include_router(tournaments.router)
    app.include_router(users.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = createApp()

if __name__ == "__main__":
    initDatabase()
