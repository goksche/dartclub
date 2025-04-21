from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    player,
    tournament,
    match,
    ranking,
    snapshot  # falls du snapshot.py schon eingebunden hast
)

app = FastAPI(
    title="Dartclub Backend",
    description="🎯 FastAPI Backend zur Turnier- und Spielerverwaltung",
    version="1.5.0"
)

# CORS (für zukünftiges Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später einschränken für Produktion
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTER registrieren
app.include_router(player.router, prefix="/player")
app.include_router(tournament.router, prefix="/tournament")
app.include_router(match.router, prefix="/match")
app.include_router(ranking.router)
app.include_router(snapshot.router)  # Optional: nur wenn Snapshot-API aktiv ist

# ROOT-ROUTE
@app.get("/")
def root():
    return {
        "message": "🚀 Dartclub Backend läuft!",
        "swagger": "/docs",
        "redoc": "/redoc"
    }
