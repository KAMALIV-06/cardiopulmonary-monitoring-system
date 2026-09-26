import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class VitalData(BaseModel):
    """
    Core Normalized Physiological Schema.
    Hardware-Independent Contract: All data sources (Simulator, hardware, Dataset)
    MUST normalize into this exact model.
    """
    patient_id: str = Field(..., description="Unique patient identifier", json_schema_extra={"example": "PATIENT-001"})
    device_id: str = Field(..., description="Ingesting device or simulator ID", json_schema_extra={"example": "SIM-001"})
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc), 
        description="UTC acquisition timestamp"
    )
    heart_rate: float = Field(..., ge=0.0, le=300.0, description="Heart rate in beats per minute")
    spo2: float = Field(..., ge=0.0, le=100.0, description="Peripheral blood oxygen saturation percentage")
    respiratory_rate: float = Field(..., ge=0.0, le=100.0, description="Breathing rate in breaths per minute")
    ppg_samples: List[float] = Field(
        default_factory=list, 
        description="PPG waveform samples (raw or normalized units)"
    )
    signal_quality: float = Field(
        ..., ge=0.0, le=1.0, 
        description="Signal Quality Index (SQI) from 0.0 (unusable) to 1.0 (clean)"
    )
    source: Literal["simulator", "dataset", "hardware"] = Field(
        ..., 
        description="Origin source of the telemetry"
    )

    @field_validator("heart_rate", "spo2", "respiratory_rate")
    @classmethod
    def round_values(cls, v: float) -> float:
        return round(float(v), 1)

class VitalReadingOut(VitalData):
    id: Optional[int] = None
    risk_score: float = 0.0
    risk_level: str = "NORMAL"

    model_config = ConfigDict(from_attributes=True)


class HistoricalVitalsResponse(BaseModel):
    patient_id: str
    count: int
    readings: List[VitalReadingOut]
