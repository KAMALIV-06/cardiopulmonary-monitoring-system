from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.hardware import HardwarePayload
from app.data_sources.hardware_adapter import HardwareAdapter
from app.api.v1.endpoints.vitals import process_and_persist_vital
from app.websocket.manager import ws_manager

router = APIRouter()
hardware_adapter = HardwareAdapter()

@router.post("/ingest/hardware", summary="ESP8266 + MAX30102 Ingestion Endpoint")
async def ingest_hardware_payload(
    payload: HardwarePayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts PPG and device-derived vitals from ESP8266 + MAX30102.
    Converts the hardware payload into normalized VitalData via HardwareAdapter,
    ensuring 100% hardware-independent downstream analysis.
    """
    # 1. Normalize hardware payload
    normalized_vital = hardware_adapter.normalize(payload)

    # Renew hardware priority; the simulator suppresses this patient's publications
    # until telemetry stops arriving for the lease window.
    ws_manager.mark_hardware_active(normalized_vital.patient_id)

    # 2. Feed into common ingestion pipeline
    return await process_and_persist_vital(normalized_vital, db)
