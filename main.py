import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.presentation.routes import (
    teams_router,
    players_router,
    scheduled_matchups_router,
    gamelogs_router
)

app = FastAPI(
    title="Draftbash-Players-API",
    description="API for NBA player stats.",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return {"message": "Draftbash Players api"}


@app.get("/ping")
async def main():
    return "Ping successful!"


# Make the routes from the routers available
app.include_router(players_router)
app.include_router(teams_router)
app.include_router(scheduled_matchups_router)
app.include_router(gamelogs_router)
