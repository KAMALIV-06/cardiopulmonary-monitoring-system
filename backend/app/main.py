import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Ensure root directory is in sys.path so simulator package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.config import settings
from app.core.logging import logger
from app.database.session import verify_database_connection
from app.api.v1.router import api_router
from app.api.v1.endpoints.simulator import register_sim_controller
from app.services.simulator_runner import simulator_controller
from app.websocket.manager import ws_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic migrations are an explicit deployment step; startup only checks connectivity.
    logger.info("Verifying PostgreSQL connection...")
    await verify_database_connection()
    
    # Wire simulator controller into API endpoints
    register_sim_controller(simulator_controller)
    
    # Auto-start simulator with normal rhythm for immediate out-of-the-box telemetry
    if settings.AUTO_START_SIMULATOR:
        logger.info("Starting background physiological simulator...")
        await simulator_controller.start()
    
    yield
    
    # Shutdown: Stop simulator
    logger.info("Stopping background physiological simulator...")
    if simulator_controller.is_running:
        await simulator_controller.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Imagine Cup 2026: Cardiopulmonary Monitoring & Early Risk Detection Telemetry Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root Healthcheck
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "database": settings.DATABASE_URL.split("://")[0],
        "simulator_active": simulator_controller.is_running,
        "active_scenario": simulator_controller.current_scenario
    }

# High-Performance WebSocket Streaming Endpoint
@app.websocket("/ws/vitals/{patient_id}")
async def websocket_vitals_endpoint(websocket: WebSocket, patient_id: str):
    origin = websocket.headers.get("origin")
    if origin and "*" not in settings.CORS_ORIGINS and origin not in settings.CORS_ORIGINS:
        await websocket.close(code=1008, reason="Origin not allowed")
        return
    await ws_manager.connect(websocket, patient_id)
    try:
        while True:
            # Client can send control messages or keepalive pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, patient_id)
    except Exception as e:
        logger.error(f"WebSocket error on patient {patient_id}: {e}")
        ws_manager.disconnect(websocket, patient_id)
