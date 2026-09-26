import json
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.session import get_db
from app.models.vital import VitalReading
from app.models.patient import Patient
from app.models.device import Device
from app.schemas.vital import VitalData, VitalReadingOut, HistoricalVitalsResponse
from app.services.signal_processing import signal_service
from app.services.risk_analyzer import risk_analyzer
from app.services.alert_service import alert_service
from app.websocket.manager import ws_manager
from app.core.logging import logger

router = APIRouter()

def _database_timestamp(timestamp: datetime.datetime) -> datetime.datetime:
    """Store UTC instants as naive UTC, matching the existing PostgreSQL schema."""
    if timestamp.tzinfo is not None:
        return timestamp.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return timestamp

async def process_and_persist_vital(vital: VitalData, db: AsyncSession) -> dict:
    """
    Core Ingestion Pipeline:
    Validation -> PPG Processing -> Rule-Based Risk Analysis -> Persist -> WebSocket Broadcast
    """
    # Drop simulator frames during a live hardware lease so they cannot become
    # a newer database row or replace hardware values on another consumer.
    if vital.source == "simulator" and ws_manager.hardware_is_active(vital.patient_id):
        return {"status": "suppressed", "reason": "hardware source has priority"}

    # 1. PPG signal processing
    filtered_ppg = signal_service.filter_ppg(vital.ppg_samples)
    # Very short windows cannot support a meaningful waveform quality estimate;
    # in that case retain the source-provided value rather than inventing one.
    calculated_sqi = (
        signal_service.calculate_sqi(filtered_ppg)
        if len(filtered_ppg) >= 100
        else vital.signal_quality
    )
    
    # Keep the normalized source waveform unchanged for persistence and display;
    # use the filtered copy only for processing and SQI estimation.
    vital.signal_quality = min(vital.signal_quality, calculated_sqi)

    # 2. Risk Analysis (CEWS / NEWS2)
    risk_result = risk_analyzer.analyze(vital)

    # 3. Ensure patient exists in DB (auto-seed if first time seen)
    patient = await db.get(Patient, vital.patient_id)
    if not patient:
        patient = Patient(
            id=vital.patient_id,
            name="Default Patient",
            age=45,
            gender="Unspecified",
            medical_record_number=f"MRN-{vital.patient_id}",
            baseline_notes="Auto-provisioned placeholder; no patient history supplied."
        )
        db.add(patient)
        await db.commit()

    stored_timestamp = _database_timestamp(vital.timestamp)
    device = await db.get(Device, vital.device_id)
    if not device:
        device = Device(
            id=vital.device_id,
            device_type=vital.source,
            status="active",
            last_seen=stored_timestamp,
        )
        db.add(device)
    else:
        device.device_type = vital.source
        device.status = "active"
        device.last_seen = stored_timestamp

    # 4. Persist Vital Reading to Database
    db_vital = VitalReading(
        patient_id=vital.patient_id,
        device_id=vital.device_id,
        timestamp=stored_timestamp,
        heart_rate=vital.heart_rate,
        spo2=vital.spo2,
        respiratory_rate=vital.respiratory_rate,
        ppg_samples_json=json.dumps(vital.ppg_samples),
        signal_quality=vital.signal_quality,
        source=vital.source,
        risk_score=risk_result.risk_score,
        risk_level=risk_result.risk_level
    )
    db.add(db_vital)
    await db.commit()
    await db.refresh(db_vital)

    # 5. Evaluate and emit clinical alerts
    new_alerts = await alert_service.evaluate_and_create_alerts(vital, risk_result, db)

    # 6. Real-time WebSocket Broadcast
    broadcast_payload = {
        "type": "VITAL_UPDATE",
        "vital": vital.model_dump(),
        "risk": risk_result.model_dump(),
        "alerts": [
            {
                "id": a.id,
                "type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "timestamp": a.timestamp.isoformat(),
                "acknowledged": a.acknowledged
            }
            for a in new_alerts
        ]
    }
    await ws_manager.broadcast_patient_telemetry(vital.patient_id, broadcast_payload)

    return {
        "status": "success",
        "id": db_vital.id,
        "risk_score": risk_result.risk_score,
        "risk_level": risk_result.risk_level,
        "alerts_generated": len(new_alerts)
    }

@router.post("/ingest/vitals", summary="Unified Ingestion Endpoint")
async def ingest_vitals(
    vital: VitalData,
    db: AsyncSession = Depends(get_db)
):
    """
    Hardware-Independent Unified Ingestion Endpoint.
    Accepts normalized VitalData from any source (Simulator, Hardware Adapter, Dataset).
    """
    if vital.source == "hardware":
        ws_manager.mark_hardware_active(vital.patient_id)
    return await process_and_persist_vital(vital, db)

@router.get("/vitals/{patient_id}/latest", response_model=Optional[VitalReadingOut])
async def get_latest_vital(
    patient_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent vital telemetry for a patient."""
    query = (
        select(VitalReading)
        .where(VitalReading.patient_id == patient_id)
        .order_by(desc(VitalReading.timestamp))
        .limit(1)
    )
    result = await db.execute(query)
    record = result.scalars().first()
    if not record:
        return None
    
    return VitalReadingOut(
        patient_id=record.patient_id,
        device_id=record.device_id,
        timestamp=record.timestamp,
        heart_rate=record.heart_rate,
        spo2=record.spo2,
        respiratory_rate=record.respiratory_rate,
        ppg_samples=json.loads(record.ppg_samples_json),
        signal_quality=record.signal_quality,
        source=record.source,
        risk_score=record.risk_score,
        risk_level=record.risk_level,
        id=record.id
    )

@router.get("/vitals/{patient_id}/history", response_model=HistoricalVitalsResponse)
async def get_vital_history(
    patient_id: str,
    limit: int = Query(default=60, ge=1, le=10000),
    window_minutes: Optional[int] = Query(default=None, ge=1, le=60),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve historical vital readings for charting."""
    query = (
        select(VitalReading)
        .where(VitalReading.patient_id == patient_id)
        .order_by(desc(VitalReading.timestamp))
        .limit(limit)
    )
    if window_minutes is not None:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=window_minutes)
        query = query.where(VitalReading.timestamp >= cutoff)
    result = await db.execute(query)
    records = result.scalars().all()
    
    readings = [
        VitalReadingOut(
            patient_id=r.patient_id,
            device_id=r.device_id,
            timestamp=r.timestamp,
            heart_rate=r.heart_rate,
            spo2=r.spo2,
            respiratory_rate=r.respiratory_rate,
            ppg_samples=json.loads(r.ppg_samples_json),
            signal_quality=r.signal_quality,
            source=r.source,
            risk_score=r.risk_score,
            risk_level=r.risk_level,
            id=r.id
        )
        for r in reversed(records)
    ]
    return HistoricalVitalsResponse(patient_id=patient_id, count=len(readings), readings=readings)
