import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class HardwarePayload(BaseModel):
    """
    Data received from an ESP8266 with a MAX30102 PPG sensor.
    The HardwareAdapter will ingest this and normalize it into VitalData.
    """
    device_id: str = Field(..., json_schema_extra={"example": "ESP8266-MAX30102-01"})
    patient_id: str = Field(default="PATIENT-001")
    timestamp: Optional[datetime.datetime] = None
    
    # MAX30102 raw optical channels and a PPG window (may be normalized)
    ppg_samples: List[float] = Field(default_factory=list)
    ppg_red_samples: Optional[List[int]] = Field(default_factory=list)
    ppg_ir_samples: Optional[List[int]] = Field(default_factory=list)
    heart_rate: float = Field(..., ge=0.0, le=300.0)
    spo2: float = Field(..., ge=0.0, le=100.0)
    signal_quality: Optional[float] = Field(default=None, ge=0.0, le=1.0)
