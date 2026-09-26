from fastapi import APIRouter
from app.api.v1.endpoints import vitals, hardware, simulator, alerts, patients

api_router = APIRouter()

api_router.include_router(vitals.router, tags=["Vitals Telemetry"])
api_router.include_router(hardware.router, tags=["Hardware Ingestion"])
api_router.include_router(simulator.router, tags=["Simulator Control"])
api_router.include_router(alerts.router, tags=["Clinical Alerts"])
api_router.include_router(patients.router, tags=["Patients"])
