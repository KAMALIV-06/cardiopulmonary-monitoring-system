from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.session import get_db
from app.models.alert import ClinicalAlert
from app.schemas.alert import AlertOut, AlertAcknowledge

router = APIRouter()

@router.get("/alerts/{patient_id}", response_model=List[AlertOut])
async def get_patient_alerts(
    patient_id: str,
    limit: int = Query(default=30, ge=1, le=100),
    unacknowledged_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve active and recent clinical alerts for a patient."""
    query = (
        select(ClinicalAlert)
        .where(ClinicalAlert.patient_id == patient_id)
        .order_by(desc(ClinicalAlert.timestamp))
    )
    if unacknowledged_only:
        query = query.where(ClinicalAlert.acknowledged == False)
    
    query = query.limit(limit)
    result = await db.execute(query)
    alerts = result.scalars().all()
    return alerts

@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertOut)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge a clinical alert."""
    alert = await db.get(ClinicalAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    await db.commit()
    await db.refresh(alert)
    return alert
