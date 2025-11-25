import logging
from uuid import UUID
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.shared.dependencies.configure_container import configure_container

from src.api.modules.interactions import interactions_routes, interactions_ws
from src.api.websocket.connections import WebsocketConnectionsContainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
    connections = WebsocketConnectionsContainer._active_connections

    return {
        "connection_ids": list(connections.keys()),
        "count": len(connections)
    }

@app.delete("/connections/{connection_id}", tags=["Internal"])
async def get_websocket_connections(
    connection_id: UUID
):
    WebsocketConnectionsContainer.remove_connection(connection_id=connection_id)

    connections = WebsocketConnectionsContainer._active_connections

    return {
        "connection_ids": list(connections.keys()),
        "count": len(connections)
    }