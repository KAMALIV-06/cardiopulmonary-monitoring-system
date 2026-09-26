import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(16), nullable=False)
    medical_record_number = Column(String(64), unique=True, index=True)
    baseline_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    vital_readings = relationship("VitalReading", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("ClinicalAlert", back_populates="patient", cascade="all, delete-orphan")
