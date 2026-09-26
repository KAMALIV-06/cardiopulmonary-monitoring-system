"""Insert an idempotent, synthetic-only cardiopulmonary demo cohort.

Run from backend after ``alembic upgrade head`` using the configured DATABASE_URL.
"""
import asyncio
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.models import (
    Allergy, ClinicalAlert, ClinicalMeasurement, Device, LabResult,
    MedicalHistory, Medication, Patient, PatientEvent, VitalReading,
)
from app.schemas.vital import VitalData
from app.services.risk_analyzer import risk_analyzer

UTC = dt.timezone.utc
TODAY = dt.datetime.now(UTC).date()

COHORT = [
    {"id":"DEMO-001","name":"Aarav Demo","age":67,"gender":"Male","height":171,"weight":78,"conditions":[("Hypertension", "Stable"),("Type 2 diabetes", "Active")],"meds":[("Amlodipine","5 mg","Once daily"),("Metformin","500 mg","Twice daily")],"allergies":[("Penicillin","Rash","Moderate")],"bp":138,"temp":36.8,"glucose":142,"hr":82,"spo2":96,"rr":17,"labs":[("HbA1c",7.2,"%","4.0–5.6%"),("Creatinine",1.0,"mg/dL","0.7–1.3")],"event":"Routine cardiopulmonary monitoring enrollment"},
    {"id":"DEMO-002","name":"Mira Demo","age":58,"gender":"Female","height":160,"weight":69,"conditions":[("Asthma history", "Stable"),("Seasonal allergic rhinitis", "Active")],"meds":[("Budesonide/formoterol","One inhalation","Twice daily")],"allergies":[("Dust mite","Wheezing","Moderate")],"bp":126,"temp":36.7,"glucose":98,"hr":76,"spo2":97,"rr":16,"labs":[("Eosinophils",0.4,"10^9/L","0.0–0.5"),("Hemoglobin",13.1,"g/dL","12.0–16.0")],"event":"Respiratory review recorded in demo history"},
    {"id":"DEMO-003","name":"Dev Demo","age":73,"gender":"Male","height":174,"weight":82,"conditions":[("Coronary artery disease", "Stable"),("Hypertension", "Active")],"meds":[("Atorvastatin","20 mg","Once nightly"),("Losartan","50 mg","Once daily")],"allergies":[("No known drug allergy","None reported","Low")],"bp":144,"temp":36.9,"glucose":109,"hr":88,"spo2":95,"rr":19,"labs":[("LDL cholesterol",104,"mg/dL","<100"),("Potassium",4.2,"mmol/L","3.5–5.1")],"event":"Prior cardiology follow-up (synthetic event)"},
    {"id":"DEMO-004","name":"Anaya Demo","age":46,"gender":"Female","height":165,"weight":72,"conditions":[("Type 2 diabetes", "Active"),("Obstructive sleep apnea history", "Stable")],"meds":[("Metformin","500 mg","Twice daily")],"allergies":[("Latex","Contact irritation","Mild")],"bp":132,"temp":36.6,"glucose":154,"hr":80,"spo2":96,"rr":18,"labs":[("HbA1c",7.8,"%","4.0–5.6%"),("TSH",2.1,"mIU/L","0.4–4.0")],"event":"Sleep clinic follow-up (synthetic event)"},
    {"id":"DEMO-005","name":"Kabir Demo","age":62,"gender":"Male","height":178,"weight":84,"conditions":[("Chronic bronchitis history", "Stable"),("Hypertension", "Active")],"meds":[("Tiotropium","18 mcg","Once daily"),("Lisinopril","10 mg","Once daily")],"allergies":[("Sulfonamide","Hives","Moderate")],"bp":136,"temp":36.8,"glucose":103,"hr":86,"spo2":94,"rr":20,"labs":[("Hemoglobin",14.0,"g/dL","13.0–17.0"),("CRP",4.8,"mg/L","<5.0")],"event":"Pulmonary follow-up (synthetic event)"},
    {"id":"DEMO-006","name":"Isha Demo","age":54,"gender":"Female","height":158,"weight":65,"conditions":[("Atrial fibrillation history", "Under review"),("Hypothyroidism", "Stable")],"meds":[("Levothyroxine","50 mcg","Once daily"),("Apixaban","5 mg","Twice daily")],"allergies":[("Adhesive dressing","Localized redness","Mild")],"bp":128,"temp":36.7,"glucose":96,"hr":92,"spo2":97,"rr":18,"labs":[("TSH",3.0,"mIU/L","0.4–4.0"),("Hemoglobin",12.8,"g/dL","12.0–16.0")],"event":"Cardiac rhythm review (synthetic event)"},
    {"id":"DEMO-007","name":"Rohan Demo","age":39,"gender":"Male","height":181,"weight":79,"conditions":[("Prior pneumonia", "Resolved"),("No ongoing cardiac history", "Historical")],"meds":[("No active medication","N/A","N/A")],"allergies":[("No known drug allergy","None reported","Low")],"bp":122,"temp":36.6,"glucose":91,"hr":72,"spo2":98,"rr":15,"labs":[("White blood cells",6.4,"10^9/L","4.0–11.0"),("CRP",1.2,"mg/L","<5.0")],"event":"Previous respiratory admission, resolved (synthetic event)"},
    {"id":"DEMO-008","name":"Tara Demo","age":69,"gender":"Female","height":154,"weight":70,"conditions":[("Heart failure history", "Under review"),("Hypertension", "Active")],"meds":[("Carvedilol","6.25 mg","Twice daily"),("Furosemide","20 mg","Once daily")],"allergies":[("Iodinated contrast","Nausea","Mild")],"bp":140,"temp":36.9,"glucose":112,"hr":90,"spo2":95,"rr":20,"labs":[("Sodium",139,"mmol/L","135–145"),("BNP",118,"pg/mL","<100")],"event":"Fluid-status review (synthetic event)"},
]


async def seed() -> None:
    now = dt.datetime.now(UTC)
    async with AsyncSessionLocal() as db:
        inserted = 0
        for index, item in enumerate(COHORT):
            existing = await db.get(Patient, item["id"])
            if existing:
                if existing.demo_data:
                    latest_result = await db.execute(
                        select(VitalReading.id).where(VitalReading.patient_id == existing.id)
                        .order_by(VitalReading.timestamp.desc()).limit(1)
                    )
                    latest_vital_id = latest_result.scalar_one_or_none()
                    if latest_vital_id:
                        alert_result = await db.execute(
                            select(ClinicalAlert).where(
                                ClinicalAlert.patient_id == existing.id,
                                ClinicalAlert.alert_type == "DEMO_REVIEW",
                                ClinicalAlert.vital_reading_id.is_(None),
                            )
                        )
                        for old_demo_alert in alert_result.scalars():
                            old_demo_alert.vital_reading_id = latest_vital_id
                continue

            patient = Patient(
                id=item["id"], name=item["name"], age=item["age"], gender=item["gender"],
                date_of_birth=TODAY.replace(year=TODAY.year-item["age"]),
                medical_record_number=f"SYN-{item['id']}", height_cm=item["height"], weight_kg=item["weight"],
                baseline_notes="Synthetic demo profile only. Not real patient information.",
                monitoring_status="active", demo_data=True,
            )
            db.add(patient)
            await db.flush()

            for condition, status in item["conditions"]:
                db.add(MedicalHistory(patient_id=patient.id, condition_name=condition,
                    diagnosis_date=TODAY-dt.timedelta(days=365*(index+1)), status=status,
                    notes="Synthetic demo history; verify all details with a clinician."))
            for name, dosage, frequency in item["meds"]:
                db.add(Medication(patient_id=patient.id, medication_name=name, dosage=dosage,
                    frequency=frequency, start_date=TODAY-dt.timedelta(days=90),
                    notes="Synthetic demo medication record; not a prescription."))
            for allergen, reaction, severity in item["allergies"]:
                db.add(Allergy(patient_id=patient.id, allergen=allergen, reaction=reaction,
                    severity=severity, notes="Synthetic demo record."))

            recorded_at = now-dt.timedelta(days=2)
            for kind, value, unit in (("Blood pressure systolic",item["bp"],"mmHg"),
                ("Blood pressure diastolic",82+index%8,"mmHg"),("Temperature",item["temp"],"°C"),
                ("Blood glucose",item["glucose"],"mg/dL")):
                db.add(ClinicalMeasurement(patient_id=patient.id, measurement_type=kind, value=value,
                    unit=unit, measured_at=recorded_at, source="CLINICAL_RECORD",
                    notes="Synthetic demo clinical record."))
            for test, value, unit, ref in item["labs"]:
                db.add(LabResult(patient_id=patient.id, test_name=test, value=value, unit=unit,
                    reference_range=ref, measured_at=recorded_at, source="CLINICAL_RECORD"))
            db.add(PatientEvent(patient_id=patient.id, event_type="DEMO_HISTORY", occurred_at=recorded_at,
                summary=item["event"], source="CLINICAL_RECORD"))

            device_id = f"DATASET-{item['id']}"
            db.add(Device(id=device_id, device_type="dataset", status="active", last_seen=now.replace(tzinfo=None)))
            patient_readings = []
            for reading_index in range(36):
                trend_offset = ((reading_index % 9)-4)
                hr = max(40, item["hr"]+trend_offset)
                spo2 = max(80, min(100, item["spo2"]-(reading_index % 4 == 0)))
                rr = max(6, item["rr"]+(reading_index % 5 == 0))
                timestamp = now-dt.timedelta(minutes=5*(35-reading_index))
                vital = VitalData(patient_id=patient.id, device_id=device_id, timestamp=timestamp,
                    heart_rate=hr, spo2=spo2, respiratory_rate=rr, ppg_samples=[],
                    signal_quality=0.92, source="dataset")
                risk = risk_analyzer.analyze(vital)
                reading = VitalReading(patient_id=patient.id, device_id=device_id,
                    timestamp=timestamp.replace(tzinfo=None), heart_rate=hr, spo2=spo2,
                    respiratory_rate=rr, ppg_samples_json="[]", signal_quality=0.92,
                    source="dataset", risk_score=risk.risk_score, risk_level=risk.risk_level)
                db.add(reading)
                patient_readings.append(reading)
            if index in (2, 5, 7):
                await db.flush()
                db.add(ClinicalAlert(patient_id=patient.id, timestamp=(now-dt.timedelta(hours=2)).replace(tzinfo=None),
                    alert_type="DEMO_REVIEW", severity="WATCH",
                    message="Synthetic historical monitoring alert; review the demo trend.", acknowledged=index != 5,
                    vital_reading_id=patient_readings[-1].id))
            inserted += 1

        await db.commit()
    print(f"Seeded {inserted} synthetic demo patients; existing IDs were left unchanged.")


if __name__ == "__main__":
    asyncio.run(seed())
