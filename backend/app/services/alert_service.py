import datetime
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.alert import ClinicalAlert
from app.schemas.vital import VitalData
from app.schemas.risk import RiskAnalysisResult
from app.schemas.alert import AlertCreate
from app.core.logging import logger


class AlertService:
    """
    Clinical alert evaluation with cooldown throttling.
    Alert severity: INFO / WATCH / HIGH (matching frontend spec).
    
    Uses persistence logic: only creates alerts when conditions persist,
    not on single noisy readings. Cooldown window prevents alert flooding.
    """

    def __init__(self):
        # Tracks last alert time per (patient_id, alert_type) to prevent spam
        self._last_alert_time: Dict[tuple, datetime.datetime] = {}
        self._cooldown_seconds = 20  # Minimum seconds between same-type alerts per patient
        # Track consecutive abnormal readings for persistence detection
        self._abnormal_count: Dict[tuple, int] = {}
        self._active_severity: Dict[tuple, str] = {}
        self._PERSISTENCE_THRESHOLD = 2  # Require 2+ consecutive abnormal readings

    async def evaluate_and_create_alerts(
        self,
        vital: VitalData,
        risk: RiskAnalysisResult,
        db: AsyncSession,
        vital_reading_id: Optional[int] = None,
    ) -> List[ClinicalAlert]:
        alerts_to_create: List[AlertCreate] = []
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        # ── SpO2 / Hypoxemia ────────────────────────────────────────────────
        if vital.spo2 > 0:
            if vital.spo2 <= 91.0:
                severity = "HIGH" if vital.spo2 <= 88.0 else "WATCH"
                alerts_to_create.append(AlertCreate(
                    patient_id=vital.patient_id,
                    alert_type="HYPOXEMIA",
                    severity=severity,
                    message=f"Abnormal low SpO2 measurement: {vital.spo2}% — clinical review recommended.",
                    trigger_value=vital.spo2
                ))
            elif vital.spo2 <= 94.0:
                alerts_to_create.append(AlertCreate(
                    patient_id=vital.patient_id,
                    alert_type="SPO2_BORDERLINE",
                    severity="WATCH",
                    message=f"SpO2 borderline: {vital.spo2}% — monitor closely",
                    trigger_value=vital.spo2
                ))

        # ── Heart Rate ──────────────────────────────────────────────────────
        if vital.heart_rate > 0:
            if vital.heart_rate >= 130.0:
                severity = "HIGH" if vital.heart_rate >= 150.0 else "WATCH"
                alerts_to_create.append(AlertCreate(
                    patient_id=vital.patient_id,
                    alert_type="TACHYCARDIA",
                    severity=severity,
                    message=f"Abnormal elevated heart-rate measurement: {vital.heart_rate} bpm — clinical review recommended.",
                    trigger_value=vital.heart_rate
                ))
            elif vital.heart_rate <= 45.0:
                alerts_to_create.append(AlertCreate(
                    patient_id=vital.patient_id,
                    alert_type="BRADYCARDIA",
                    severity="HIGH",
                    message=f"Abnormal low heart-rate measurement: {vital.heart_rate} bpm — clinical review recommended.",
                    trigger_value=vital.heart_rate
                ))

        # ── Respiratory Rate ────────────────────────────────────────────────
        if vital.respiratory_rate > 0:
            if vital.respiratory_rate >= 26.0:
                alerts_to_create.append(AlertCreate(
                    patient_id=vital.patient_id,
                    alert_type="TACHYPNEA",
                    severity="HIGH",
                    message=f"Abnormal elevated respiratory-rate measurement: {vital.respiratory_rate} /min — clinical review recommended.",
                    trigger_value=vital.respiratory_rate
                ))
            elif vital.respiratory_rate >= 22.0:
                alerts_to_create.append(AlertCreate(
                    patient_id=vital.patient_id,
                    alert_type="TACHYPNEA_WATCH",
                    severity="WATCH",
                    message=f"Respiratory rate elevated: {vital.respiratory_rate} /min — monitor for fatigue",
                    trigger_value=vital.respiratory_rate
                ))
            elif vital.respiratory_rate <= 8.0:
                alerts_to_create.append(AlertCreate(
                    patient_id=vital.patient_id,
                    alert_type="BRADYPNEA",
                    severity="HIGH",
                    message=f"Low respiratory rate: {vital.respiratory_rate} /min — possible hypoventilation",
                    trigger_value=vital.respiratory_rate
                ))

        # ── PPG Signal Quality ────────────────────────────────────────────────
        if vital.signal_quality < 0.2:
            alerts_to_create.append(AlertCreate(
                patient_id=vital.patient_id,
                alert_type="SENSOR_SIGNAL_LOW",
                severity="INFO",
                message="PPG signal quality is critically low — check optical sensor contact and motion",
                trigger_value=vital.signal_quality
            ))

        # ── Create alerts with cooldown and persistence filtering ───────────
        created_alerts: List[ClinicalAlert] = []
        severity_rank = {"INFO": 0, "WATCH": 1, "HIGH": 2}
        for alert_data in alerts_to_create:
            key = (alert_data.patient_id, alert_data.alert_type)

            # Persistence counter: require consecutive abnormal readings
            self._abnormal_count[key] = self._abnormal_count.get(key, 0) + 1
            if self._abnormal_count[key] < self._PERSISTENCE_THRESHOLD:
                continue  # Not yet persistent — wait for next reading

            previous_severity = self._active_severity.get(key)
            if previous_severity and severity_rank[alert_data.severity] <= severity_rank[previous_severity]:
                continue  # Same state is already active; emit only on escalation.

            # Cooldown: don't spam the same alert
            last_time = self._last_alert_time.get(key)
            if not previous_severity and last_time and (now - last_time).total_seconds() < self._cooldown_seconds:
                continue

            self._last_alert_time[key] = now
            db_alert = ClinicalAlert(
                patient_id=alert_data.patient_id,
                timestamp=now,
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                message=alert_data.message,
                trigger_value=alert_data.trigger_value,
                vital_reading_id=vital_reading_id,
                acknowledged=False
            )
            db.add(db_alert)
            created_alerts.append(db_alert)
            self._active_severity[key] = alert_data.severity
            logger.warning(
                f"ALERT [{alert_data.severity}] {vital.patient_id}: {alert_data.message}"
            )

        # Reset persistence counters for non-triggered alert types this cycle
        triggered_types = {(a.patient_id, a.alert_type) for a in alerts_to_create}
        keys_to_reset = [k for k in self._abnormal_count if k not in triggered_types and k[0] == vital.patient_id]
        for k in keys_to_reset:
            self._abnormal_count[k] = 0
            self._active_severity.pop(k, None)

        if created_alerts:
            await db.commit()
            for a in created_alerts:
                await db.refresh(a)

        return created_alerts


alert_service = AlertService()
