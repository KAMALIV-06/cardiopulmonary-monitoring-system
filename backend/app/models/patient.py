import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Date, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(16), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    medical_record_number = Column(String(64), unique=True, index=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    baseline_notes = Column(Text, nullable=True)
    monitoring_status = Column(String(24), nullable=False, default="active", server_default="active")
    demo_data = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))

    vital_readings = relationship("VitalReading", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("ClinicalAlert", back_populates="patient", cascade="all, delete-orphan")
    medical_history = relationship("MedicalHistory", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="patient", cascade="all, delete-orphan")
    clinical_measurements = relationship("ClinicalMeasurement", back_populates="patient", cascade="all, delete-orphan")
    lab_results = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")
    patient_events = relationship("PatientEvent", back_populates="patient", cascade="all, delete-orphan")
