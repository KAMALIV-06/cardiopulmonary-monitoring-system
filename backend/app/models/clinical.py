from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.base import Base


class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    condition_name = Column(String(128), nullable=False)
    diagnosis_date = Column(Date, nullable=True)
    status = Column(String(32), nullable=False, default="active")
    notes = Column(Text, nullable=True)
    patient = relationship("Patient", back_populates="medical_history")


class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    medication_name = Column(String(128), nullable=False)
    dosage = Column(String(64), nullable=False)
    frequency = Column(String(128), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    patient = relationship("Patient", back_populates="medications")


class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    allergen = Column(String(128), nullable=False)
    reaction = Column(String(128), nullable=False)
    severity = Column(String(24), nullable=False)
    notes = Column(Text, nullable=True)
    patient = relationship("Patient", back_populates="allergies")


class ClinicalMeasurement(Base):
    __tablename__ = "clinical_measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    measurement_type = Column(String(64), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)
    measured_at = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(32), nullable=False, default="CLINICAL_RECORD")
    notes = Column(Text, nullable=True)
    patient = relationship("Patient", back_populates="clinical_measurements")


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    test_name = Column(String(128), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)
    reference_range = Column(String(64), nullable=True)
    measured_at = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(32), nullable=False, default="CLINICAL_RECORD")
    notes = Column(Text, nullable=True)
    patient = relationship("Patient", back_populates="lab_results")


class PatientEvent(Base):
    __tablename__ = "patient_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(32), nullable=False, default="CLINICAL_RECORD")
    patient = relationship("Patient", back_populates="patient_events")
