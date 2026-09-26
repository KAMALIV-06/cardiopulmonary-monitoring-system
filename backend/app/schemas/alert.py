import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class AlertCreate(BaseModel):
    patient_id: str
    alert_type: str
    severity: str  # "INFO", "WATCH", "HIGH"
    message: str
    trigger_value: Optional[float] = None

class AlertOut(AlertCreate):
    id: int
    timestamp: datetime.datetime
    acknowledged: bool
    vital_reading_id: Optional[int] = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def mark_legacy_utc(cls, value):
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value

    model_config = ConfigDict(from_attributes=True)


class AlertAcknowledge(BaseModel):
    acknowledged: bool = True
