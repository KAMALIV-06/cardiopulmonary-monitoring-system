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

def test_low_spo2_and_multiple_findings_raise_early_warning():
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
    assert any("spo2" in a.lower() for a in risk.anomalies)
    assert "SpO2" in risk.suggested_action

def test_very_low_heart_rate_risk():
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
    assert any("heart-rate" in a.lower() for a in risk.anomalies)


def test_suggested_action_uses_highest_severity_finding():
    vital = VitalData(
        patient_id="P-PRIORITY", device_id="SIM-1", heart_rate=150.0,
        spo2=86.0, respiratory_rate=30.0, ppg_samples=[], signal_quality=0.95,
        source="simulator",
    )
    risk = risk_analyzer.analyze(vital)
    assert risk.suggested_action.startswith("Very low SpO2 measurement")


def test_naive_vital_timestamps_are_serialized_as_utc():
    import datetime
    vital = VitalData(
        patient_id="P-UTC", device_id="SIM-1", timestamp=datetime.datetime(2026, 1, 1),
        heart_rate=72, spo2=98, respiratory_rate=15, ppg_samples=[],
        signal_quality=0.9, source="simulator",
    )
    assert vital.timestamp.tzinfo == datetime.timezone.utc
