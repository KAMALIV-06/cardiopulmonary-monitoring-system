import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.base import Base

class ClinicalAlert(Base):
    __tablename__ = "clinical_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    alert_type = Column(String(64), nullable=False)   # e.g. HYPOXEMIA, TACHYCARDIA, TACHYPNEA, SENSOR_SIGNAL_LOW
    severity = Column(String(16), nullable=False)     # "INFO", "WATCH", "HIGH"
    message = Column(String(256), nullable=False)
    trigger_value = Column(Float, nullable=True)
    acknowledged = Column(Boolean, default=False)
    
    patient = relationship("Patient", back_populates="alerts")

    __table_args__ = (
        Index("idx_alert_patient_ack", "patient_id", "acknowledged"),
    )
