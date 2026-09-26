import pytest
from app.schemas.vital import VitalData
from app.services.risk_analyzer import risk_analyzer

def test_normal_vitals_risk():
    vital = VitalData(
        patient_id="P-NORM",
        device_id="SIM-1",
        heart_rate=72.0,
        spo2=98.0,
        respiratory_rate=14.0,
        ppg_samples=[0.1, 0.2, 1.2, -0.2],
        signal_quality=0.98,
        source="simulator"
    )
    risk = risk_analyzer.analyze(vital)
    assert risk.risk_level == "NORMAL"
    assert risk.risk_score <= 25.0

def test_acute_hypoxemia_risk():
    vital = VitalData(
        patient_id="P-HYPOX",
        device_id="SIM-1",
        heart_rate=115.0,
        spo2=86.0,
        respiratory_rate=29.0,
        ppg_samples=[0.1, 0.2, 1.2, -0.2],
        signal_quality=0.95,
        source="simulator"
    )
    risk = risk_analyzer.analyze(vital)
    assert risk.risk_level == "HIGH_RISK"
    assert any("hypoxemia" in a.lower() for a in risk.anomalies)

def test_severe_bradycardia_risk():
    vital = VitalData(
        patient_id="P-BRADY",
        device_id="SIM-1",
        heart_rate=36.0,
        spo2=96.0,
        respiratory_rate=12.0,
        ppg_samples=[0.1, 0.2, 1.2, -0.2],
        signal_quality=0.95,
        source="simulator"
    )
    risk = risk_analyzer.analyze(vital)
    assert risk.risk_level == "HIGH_RISK"
    assert any("bradycardia" in a.lower() for a in risk.anomalies)
