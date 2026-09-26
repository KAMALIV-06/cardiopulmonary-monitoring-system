import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.base import Base

class VitalReading(Base):
    __tablename__ = "vital_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id"), nullable=False, index=True)
    device_id = Column(String(64), ForeignKey("devices.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Normalized Core Vitals
    heart_rate = Column(Float, nullable=False)
    spo2 = Column(Float, nullable=False)
    respiratory_rate = Column(Float, nullable=False)
    ppg_samples_json = Column(Text, nullable=False, default="[]")  # Serialized PPG sample window
    legacy_ecg_samples_json = Column(Text, nullable=True)  # Preserves pre-PPG records; excluded from live API.
    signal_quality = Column(Float, nullable=False)   # 0.0 to 1.0
    source = Column(String(32), nullable=False)       # "simulator", "dataset", "hardware"
    
    # Derived Risk Metrics
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(16), default="NORMAL") # "NORMAL", "WATCH", "HIGH_RISK"
    
    patient = relationship("Patient", back_populates="vital_readings")
    device = relationship("Device", back_populates="vital_readings")

    __table_args__ = (
        Index("idx_patient_timestamp", "patient_id", "timestamp"),
    )
