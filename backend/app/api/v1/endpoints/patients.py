from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientOut

router = APIRouter()

@router.get("/patients", response_model=List[PatientOut])
async def list_patients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient))
    return result.scalars().all()

@router.post("/patients", response_model=PatientOut)
async def create_patient(payload: PatientCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.get(Patient, payload.id)
    if existing:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    
    patient = Patient(
        id=payload.id,
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        medical_record_number=payload.medical_record_number,
        baseline_notes=payload.baseline_notes
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient

@router.get("/patients/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
