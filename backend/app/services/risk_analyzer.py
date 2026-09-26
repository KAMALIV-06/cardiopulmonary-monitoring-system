from typing import List, Dict, Protocol
from app.schemas.vital import VitalData
from app.schemas.risk import RiskAnalysisResult
from app.services.signal_processing import signal_service


class RiskModel(Protocol):
    """Interface for a replaceable early-warning risk model."""

    def analyze(self, vital: VitalData) -> RiskAnalysisResult: ...


class BaselineRiskModel:
    """
    Rule-based Cardiopulmonary Early Warning Score (CEWS) Engine.
    Implements transparent NEWS2-derived multi-parameter risk scoring.

    IMPORTANT: This is a BASELINE RULE-BASED model — NOT a trained AI/ML classifier.
    Risk levels are indicative early warnings only and do not constitute medical diagnosis.
    Designed for easy replacement with a trained ML model via the RiskModel interface.

    Output risk levels: NORMAL / WATCH / HIGH_RISK
    """

    def analyze(self, vital: VitalData) -> RiskAnalysisResult:
        raw_score = 0
        contributing_factors: List[str] = []
        stable_factors: List[str] = []

        # ── 1. Heart Rate Evaluation (NEWS2 Subscore) ──────────────────────
        hr = vital.heart_rate
        if hr <= 0.0:
            pass  # Leads off / no signal — handled by SQI check
        elif hr <= 40:
            raw_score += 3
            contributing_factors.append("Severe bradycardia (HR ≤ 40 bpm)")
        elif hr <= 50:
            raw_score += 1
            contributing_factors.append("Mild bradycardia (HR 41–50 bpm)")
        elif hr <= 90:
            stable_factors.append("Heart rate stable")
        elif hr <= 110:
            raw_score += 1
            contributing_factors.append("Borderline tachycardia (HR 91–110 bpm)")
        elif hr <= 130:
            raw_score += 2
            contributing_factors.append("Tachycardia (HR 111–130 bpm)")
        else:
            raw_score += 3
            contributing_factors.append("Severe tachycardia (HR > 130 bpm)")

        # ── 2. SpO2 Evaluation ─────────────────────────────────────────────
        spo2 = vital.spo2
        if spo2 <= 0.0:
            pass  # No signal
        elif spo2 <= 91:
            raw_score += 3
            contributing_factors.append("Severe hypoxemia (SpO2 ≤ 91%)")
        elif spo2 <= 93:
            raw_score += 2
            contributing_factors.append("Moderate hypoxemia (SpO2 92–93%)")
        elif spo2 <= 95:
            raw_score += 1
            contributing_factors.append("Borderline hypoxemia (SpO2 94–95%)")
        else:
            stable_factors.append("SpO2 stable")

        # ── 3. Respiratory Rate Evaluation ─────────────────────────────────
        rr = vital.respiratory_rate
        if rr <= 0.0:
            pass  # No signal
        elif rr <= 8:
            raw_score += 3
            contributing_factors.append("Severe bradypnea (RR ≤ 8 /min)")
        elif rr <= 11:
            raw_score += 1
            contributing_factors.append("Mild bradypnea (RR 9–11 /min)")
        elif rr <= 20:
            stable_factors.append("Respiratory rate stable")
        elif rr <= 24:
            raw_score += 2
            contributing_factors.append("Tachypnea (RR 21–24 /min)")
        else:
            raw_score += 3
            contributing_factors.append("Severe tachypnea / respiratory distress (RR ≥ 25 /min)")

        # ── 4. Signal Quality ───────────────────────────────────────────────
        sqi = vital.signal_quality
        if sqi < 0.2:
            contributing_factors.append("Poor PPG signal quality — check optical sensor contact or motion")
        elif sqi >= 0.85:
            stable_factors.append("Signal quality good")

        # ── 5. Normalize score 0–100 (max raw ~9) ──────────────────────────
        normalized_score = min(100.0, round((raw_score / 9.0) * 100.0, 1))

        # ── 6. Risk Level: 3-tier NORMAL / WATCH / HIGH_RISK ───────────────
        # Hard critical override for dangerous physiological extremes
        is_critical_override = (
            (hr > 0 and (hr <= 40 or hr >= 140)) or
            (spo2 > 0 and spo2 <= 88) or
            (rr > 0 and (rr <= 6 or rr >= 28))
        )

        if normalized_score >= 55.0 or is_critical_override:
            risk_level = "HIGH_RISK"
        elif normalized_score >= 20.0:
            risk_level = "WATCH"
        else:
            risk_level = "NORMAL"

        # ── 7. Build display factors list ───────────────────────────────────
        display_factors: List[str] = []
        for f in contributing_factors:
            display_factors.append(f"⚠ {f}")
        for f in stable_factors:
            display_factors.append(f"✓ {f}")

        if not display_factors:
            display_factors = [
                "✓ Heart rate stable",
                "✓ SpO2 stable",
                "✓ Respiratory rate stable",
                "✓ Signal quality good",
            ]

        # ── 8. HRV — synthetic estimate from HR (real HRV requires multi-beat data)
        # The incoming waveform is usually only a half-second chunk; don't invent
        # HRV measurements from a single reported heart-rate value.
        hrv = signal_service.analyze_hrv([])

        return RiskAnalysisResult(
            risk_score=normalized_score,
            risk_level=risk_level,
            confidence=round(sqi, 2),
            contributing_factors=contributing_factors,
            anomalies=contributing_factors if contributing_factors else ["Normal cardiopulmonary function"],
            recommendations=display_factors,
            hrv_metrics=hrv,
            signal_sqi=sqi
        )


risk_analyzer: RiskModel = BaselineRiskModel()
# Backwards-compatible name retained for existing imports.
CardiopulmonaryRiskAnalyzer = BaselineRiskModel
