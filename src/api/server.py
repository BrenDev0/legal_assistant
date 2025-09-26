from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.dependencies.configure_container import configure_container
from src.dependencies.services import get_websocket_service

from src.api.modules.interactions import interactions_routes, interactions_ws
from src.api.modules.websocket.websocket_service import WebsocketService

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_container()  
    yield

app = FastAPI(lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://expertise-v2.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Internal"])
async def health():
    """
    ## Health check 
    This endpoints verifies server status.
    """
    return {"status": "ok"}

app.include_router(interactions_routes.router)
app.include_router(interactions_ws.router)

@app.get("/connections", tags=["Internal"])
async def get_websocket_connections():
    service = get_websocket_service()

    connections = service.active_connections

    return {
        "connection_ids": list(connections.keys()),
        "count": len(connections)
    }