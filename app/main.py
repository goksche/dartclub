from fastapi import FastAPI
from app.db import Base, engine
from app.routers import player, tournament, match

# DB Initialisierung
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dartclub Verwaltung", version="1.0.0")

# Routen registrieren
app.include_router(player.router, prefix="/player", tags=["Spieler"])
app.include_router(tournament.router, prefix="/tournament", tags=["Turniere"])

@app.get("/ping", tags=["System"])
def ping():
    return {"status": "OK 🟢"}

from app.routers import match  # oben ergänzen
app.include_router(match.router, prefix="/match", tags=["Matches"])  # unten ergänzen
