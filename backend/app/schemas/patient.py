import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PatientBase(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    medical_record_number: str
    baseline_notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientOut(PatientBase):
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

