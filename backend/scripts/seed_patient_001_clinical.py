"""Seed the synthetic clinical profile for the live PATIENT-001 hardware demo.

Run from ``backend`` with ``.venv\\Scripts\\python.exe scripts/seed_patient_001_clinical.py``.
This script adds only missing, explicitly synthetic clinical records and never
changes vital readings or alerts.
"""
import asyncio
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.models.clinical import (
    Allergy, ClinicalMeasurement, LabResult, MedicalHistory, Medication, PatientEvent,
)
from app.models.patient import Patient

PATIENT_ID = "PATIENT-001"
MARKER = "Synthetic demo clinical record. Not real patient information."
DEMO_DATE = dt.date(2026, 9, 20)
DEMO_TIME = dt.datetime(2026, 9, 20, 10, 0, tzinfo=dt.timezone.utc)


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        patient = await db.get(Patient, PATIENT_ID)
        if patient is None:
            patient = Patient(
                id=PATIENT_ID, name="Jordan Demo", age=62, gender="Male",
                date_of_birth=dt.date(1964, 9, 20), medical_record_number="MRN-DEMO-PATIENT-001",
                height_cm=172.0, weight_kg=79.0,
                baseline_notes=MARKER, monitoring_status="active", demo_data=True,
            )
            db.add(patient)
            await db.flush()
        elif patient.baseline_notes and patient.baseline_notes.startswith("Auto-provisioned placeholder"):
            # The known auto-created placeholder has no supplied identity to preserve.
            patient.name = "Jordan Demo"
            patient.age = 62
            patient.gender = "Male"
            patient.date_of_birth = dt.date(1964, 9, 20)
            patient.medical_record_number = "MRN-DEMO-PATIENT-001"
            patient.height_cm = 172.0
            patient.weight_kg = 79.0
            patient.baseline_notes = MARKER
            patient.demo_data = True

        history = [
            ("Hypertension", "Active", "Managed in this synthetic scenario."),
            ("Chronic obstructive pulmonary disease", "Stable", "Synthetic history for monitoring demonstration."),
            ("Coronary artery disease", "Under review", "Synthetic historical diagnosis; not a real patient record."),
        ]
        for condition, status, notes in history:
            await add_if_missing(db, MedicalHistory, condition_name=condition,
                                 diagnosis_date=DEMO_DATE, status=status,
                                 notes=f"{notes} {MARKER}")

        medications = [
            ("Demo medication: amlodipine", "5 mg", "Once daily"),
            ("Demo medication: tiotropium", "18 mcg", "Once daily"),
            ("Demo medication: atorvastatin", "20 mg", "Once nightly"),
        ]
        for name, dosage, frequency in medications:
            await add_if_missing(db, Medication, medication_name=name, dosage=dosage,
                                 frequency=frequency, start_date=DEMO_DATE,
                                 notes=f"Synthetic demo entry; not an actual prescription. {MARKER}")

        allergies = [
            ("Demo: penicillin", "Rash", "Moderate"),
            ("Demo: adhesive dressing", "Localized redness", "Mild"),
        ]
        for allergen, reaction, severity in allergies:
            await add_if_missing(db, Allergy, allergen=allergen, reaction=reaction,
                                 severity=severity, notes=MARKER)

        measurements = [
            ("blood_pressure_systolic", 132, "mmHg"),
            ("blood_pressure_diastolic", 82, "mmHg"),
            ("temperature", 36.8, "°C"),
            ("blood_glucose", 108, "mg/dL"),
        ]
        for measurement_type, value, unit in measurements:
            await add_if_missing(db, ClinicalMeasurement, measurement_type=measurement_type,
                                 value=value, unit=unit, measured_at=DEMO_TIME,
                                 source="SYNTHETIC_DEMO", notes=MARKER)

        labs = [
            ("Hemoglobin", 14.1, "g/dL", "13.0–17.0"),
            ("Creatinine", 0.9, "mg/dL", "0.7–1.3"),
            ("BNP", 86.0, "pg/mL", "<100"),
        ]
        for name, value, unit, reference in labs:
            await add_if_missing(db, LabResult, test_name=name, value=value, unit=unit,
                                 reference_range=reference, measured_at=DEMO_TIME,
                                 source="SYNTHETIC_DEMO", notes=MARKER)

        event_summary = f"Synthetic cardiopulmonary monitoring review completed. {MARKER}"
        existing_event = await db.scalar(select(PatientEvent.id).where(
            PatientEvent.patient_id == PATIENT_ID, PatientEvent.summary == event_summary
        ))
        if existing_event is None:
            db.add(PatientEvent(patient_id=PATIENT_ID, event_type="DEMO_REVIEW",
                                occurred_at=DEMO_TIME, summary=event_summary,
                                source="SYNTHETIC_DEMO"))
        await db.commit()
        print("PATIENT-001 synthetic clinical profile seeded; existing records and telemetry preserved.")


async def add_if_missing(db, model, **values) -> None:
    query = select(model.id).where(model.patient_id == PATIENT_ID)
    for key in values:
        if key != "notes":
            query = query.where(getattr(model, key) == values[key])
    query = query.where(model.notes.contains(MARKER))
    if await db.scalar(query) is None:
        db.add(model(patient_id=PATIENT_ID, **values))


if __name__ == "__main__":
    asyncio.run(seed())
