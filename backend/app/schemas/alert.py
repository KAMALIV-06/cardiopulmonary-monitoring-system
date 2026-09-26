import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class AlertAcknowledge(BaseModel):
    acknowledged: bool = True
