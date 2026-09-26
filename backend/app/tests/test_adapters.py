import pytest
from app.schemas.vital import VitalData
from app.data_sources.simulator_adapter import SimulatorAdapter
from app.data_sources.hardware_adapter import HardwareAdapter
from app.data_sources.dataset_adapter import DatasetAdapter
from app.schemas.hardware import HardwarePayload
from app.main import app

def test_simulator_adapter_normalization():
    adapter = SimulatorAdapter()
    raw = {
        "patient_id": "TEST-PATIENT-1",
        "device_id": "SIM-01",
        "heart_rate": 78.4,
        "spo2": 98.1,
        "respiratory_rate": 14.5,
        "ppg_samples": [0.12, 0.45, 1.25, -0.3],
        "signal_quality": 0.95
    }
    vital = adapter.normalize(raw)
    assert isinstance(vital, VitalData)
    assert vital.source == "simulator"
    assert vital.patient_id == "TEST-PATIENT-1"
    assert len(vital.ppg_samples) == 4
    assert vital.heart_rate == 78.4

def test_hardware_adapter_normalization():
    adapter = HardwareAdapter()
    raw_payload = HardwarePayload(
        device_id="ESP8266-MAX30102-01",
        patient_id="TEST-PATIENT-2",
        ppg_samples=[float(x) for x in range(100)],
        signal_quality=0.95,
        heart_rate=82.0,
        spo2=97.0
    )
    vital = adapter.normalize(raw_payload)
    assert isinstance(vital, VitalData)
    assert vital.source == "hardware"
    assert vital.patient_id == "TEST-PATIENT-2"
    assert len(vital.ppg_samples) == 100
    assert vital.signal_quality >= 0.9
    assert vital.respiratory_rate == 0.0  # Too little waveform history for an estimate.

def test_hardware_adapter_unavailable_sensor():
    adapter = HardwareAdapter()
    raw_payload = HardwarePayload(
        device_id="ESP8266-MAX30102-01",
        patient_id="TEST-PATIENT-2",
        ppg_samples=[],
        signal_quality=0.05,
        heart_rate=0.0,
        spo2=0.0
    )
    vital = adapter.normalize(raw_payload)
    assert isinstance(vital, VitalData)
    assert vital.source == "hardware"
    assert vital.signal_quality <= 0.1


def test_existing_hardware_ingest_route_remains_registered():
    operation = app.openapi()["paths"]["/api/v1/ingest/hardware"]
    assert "post" in operation

def test_dataset_adapter_normalization():
    adapter = DatasetAdapter()
    raw = {
        "patient_id": "MIT-BIH-100",
        "device_id": "PHYSIONET-READER",
        "heart_rate": 65.0,
        "spo2": 99.0,
        "respiratory_rate": 13.0,
        "ppg_samples": [0.1, 0.2, 0.8]
    }
    vital = adapter.normalize(raw)
    assert isinstance(vital, VitalData)
    assert vital.source == "dataset"
