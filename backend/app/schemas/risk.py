from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

class RiskAnalysisResult(BaseModel):
    """
    Cardiopulmonary Early Warning Score (CEWS) & Anomaly Assessment.
    """
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Compound risk score from 0 (Healthy) to 100 (Critical)")
    risk_level: Literal["NORMAL", "WATCH", "HIGH_RISK"] = Field(..., description="Baseline early warning tier; not a diagnosis")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Signal-quality confidence estimate")
    contributing_factors: List[str] = Field(default_factory=list)
    anomalies: List[str] = Field(default_factory=list, description="Specific identified clinical anomalies")
    recommendations: List[str] = Field(default_factory=list, description="Immediate clinical recommendations")
    hrv_metrics: Optional[Dict[str, float]] = Field(default_factory=dict, description="SDNN, RMSSD, RR-Interval")
    signal_sqi: float = Field(default=1.0, description="Signal Quality Index of the analysis window")
