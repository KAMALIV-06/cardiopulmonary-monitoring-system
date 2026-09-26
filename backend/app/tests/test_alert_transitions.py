import pytest
import datetime

from app.schemas.risk import RiskAnalysisResult
from app.schemas.vital import VitalData
from app.services.alert_service import AlertService
from app.schemas.alert import AlertOut


class FakeSession:
    def __init__(self):
        self.rows = []

    def add(self, row):
        self.rows.append(row)

    async def commit(self):
        pass

    async def refresh(self, row):
        row.id = len(self.rows)


@pytest.mark.asyncio
async def test_alerts_are_created_on_persistence_and_not_repeated_for_same_state():
    service = AlertService()
    db = FakeSession()
    vital = VitalData(
        patient_id="DEMO-ALERT", device_id="ESP8266-MAX30102-01",
        heart_rate=80, spo2=87, respiratory_rate=18, ppg_samples=[],
        signal_quality=0.9, source="hardware",
    )
    risk = RiskAnalysisResult(risk_score=55, risk_level="HIGH_RISK", confidence=0.9)

    assert await service.evaluate_and_create_alerts(vital, risk, db, 101) == []
    first = await service.evaluate_and_create_alerts(vital, risk, db, 102)
    repeated = await service.evaluate_and_create_alerts(vital, risk, db, 103)

    assert len(first) == 1
    assert first[0].vital_reading_id == 102
    assert repeated == []
    assert len(db.rows) == 1


def test_naive_alert_timestamps_are_returned_as_utc():
    alert = AlertOut(
        id=1, patient_id="DEMO-UTC", alert_type="REVIEW", severity="WATCH",
        message="Clinical review recommended.", timestamp=datetime.datetime(2026, 1, 1),
        acknowledged=False,
    )
    assert alert.timestamp.tzinfo == datetime.timezone.utc
