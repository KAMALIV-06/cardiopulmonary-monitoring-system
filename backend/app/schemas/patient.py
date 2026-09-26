import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator

class PatientBase(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    medical_record_number: Optional[str] = None
    baseline_notes: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    monitoring_status: str = "active"
    demo_data: bool = False

class PatientCreate(PatientBase):
    pass

class PatientOut(PatientBase):
    created_at: datetime.datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def mark_legacy_utc(cls, value):
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value

    model_config = ConfigDict(from_attributes=True)


class MedicalHistoryOut(BaseModel):
    id: int
    patient_id: str
    condition_name: str
    diagnosis_date: Optional[datetime.date] = None
    status: str
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class MedicationOut(BaseModel):
    id: int
    patient_id: str
    medication_name: str
    dosage: str
    frequency: str
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class AllergyOut(BaseModel):
    id: int
    patient_id: str
    allergen: str
    reaction: str
    severity: str
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ClinicalMeasurementOut(BaseModel):
    id: int
    patient_id: str
    measurement_type: str
    value: float
    unit: str
    measured_at: datetime.datetime
    source: str
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class LabResultOut(BaseModel):
    id: int
    patient_id: str
    test_name: str
    value: float
    unit: str
    reference_range: Optional[str] = None
    measured_at: datetime.datetime
    source: str
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class PatientEventOut(BaseModel):
    id: int
    patient_id: str
    event_type: str
    occurred_at: datetime.datetime
    summary: str
    source: str
    model_config = ConfigDict(from_attributes=True)


class PatientProfileOut(BaseModel):
    patient: PatientOut
    medical_history: List[MedicalHistoryOut]
    medications: List[MedicationOut]
    allergies: List[AllergyOut]
    clinical_measurements: List[ClinicalMeasurementOut]
    lab_results: List[LabResultOut]
    events: List[PatientEventOut]
