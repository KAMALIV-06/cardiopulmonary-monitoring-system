from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.patient import Patient
from app.models.clinical import Allergy, ClinicalMeasurement, LabResult, MedicalHistory, Medication, PatientEvent
from app.schemas.patient import (
    AllergyOut, ClinicalMeasurementOut, LabResultOut, MedicalHistoryOut,
    MedicationOut, PatientCreate, PatientEventOut, PatientOut, PatientProfileOut,
)

router = APIRouter()

@router.get("/patients", response_model=List[PatientOut])
async def list_patients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).order_by(Patient.id))
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
        baseline_notes=payload.baseline_notes,
        date_of_birth=payload.date_of_birth,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        monitoring_status=payload.monitoring_status,
        demo_data=payload.demo_data,
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


async def _patient_or_404(patient_id: str, db: AsyncSession) -> Patient:
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


async def _rows(db: AsyncSession, model, patient_id: str, sort_column):
    result = await db.execute(
        select(model).where(model.patient_id == patient_id).order_by(sort_column.desc())
    )
    return result.scalars().all()


@router.get("/patients/{patient_id}/profile", response_model=PatientProfileOut)
async def get_patient_profile(patient_id: str, db: AsyncSession = Depends(get_db)):
    """Return patient demographics and synthetic/clinical-record context as one profile."""
    patient = await _patient_or_404(patient_id, db)
    history = await _rows(db, MedicalHistory, patient_id, MedicalHistory.diagnosis_date)
    medications = await _rows(db, Medication, patient_id, Medication.start_date)
    allergies = await _rows(db, Allergy, patient_id, Allergy.id)
    measurements = await _rows(db, ClinicalMeasurement, patient_id, ClinicalMeasurement.measured_at)
    labs = await _rows(db, LabResult, patient_id, LabResult.measured_at)
    events = await _rows(db, PatientEvent, patient_id, PatientEvent.occurred_at)
    return PatientProfileOut(
        patient=patient,
        medical_history=history,
        medications=medications,
        allergies=allergies,
        clinical_measurements=measurements,
        lab_results=labs,
        events=events,
    )


@router.get("/patients/{patient_id}/clinical-history", response_model=List[MedicalHistoryOut])
async def get_clinical_history(patient_id: str, db: AsyncSession = Depends(get_db)):
    await _patient_or_404(patient_id, db)
    return await _rows(db, MedicalHistory, patient_id, MedicalHistory.diagnosis_date)


@router.get("/patients/{patient_id}/medications", response_model=List[MedicationOut])
async def get_medications(patient_id: str, db: AsyncSession = Depends(get_db)):
    await _patient_or_404(patient_id, db)
    return await _rows(db, Medication, patient_id, Medication.start_date)


@router.get("/patients/{patient_id}/allergies", response_model=List[AllergyOut])
async def get_allergies(patient_id: str, db: AsyncSession = Depends(get_db)):
    await _patient_or_404(patient_id, db)
    return await _rows(db, Allergy, patient_id, Allergy.id)


@router.get("/patients/{patient_id}/clinical-measurements", response_model=List[ClinicalMeasurementOut])
async def get_clinical_measurements(patient_id: str, db: AsyncSession = Depends(get_db)):
    await _patient_or_404(patient_id, db)
    return await _rows(db, ClinicalMeasurement, patient_id, ClinicalMeasurement.measured_at)


@router.get("/patients/{patient_id}/labs", response_model=List[LabResultOut])
async def get_lab_results(patient_id: str, db: AsyncSession = Depends(get_db)):
    await _patient_or_404(patient_id, db)
    return await _rows(db, LabResult, patient_id, LabResult.measured_at)


@router.get("/patients/{patient_id}/events", response_model=List[PatientEventOut])
async def get_patient_events(patient_id: str, db: AsyncSession = Depends(get_db)):
    await _patient_or_404(patient_id, db)
    return await _rows(db, PatientEvent, patient_id, PatientEvent.occurred_at)
