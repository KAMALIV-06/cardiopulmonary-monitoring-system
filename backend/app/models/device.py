import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(String(64), primary_key=True, index=True)
    device_type = Column(String(32), default="simulator")  # "simulator", "hardware", "dataset"
    mac_address = Column(String(32), nullable=True)
    status = Column(String(16), default="active")  # "active", "offline", "degraded"
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    vital_readings = relationship("VitalReading", back_populates="device")
