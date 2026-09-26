export type VitalSource = 'simulator' | 'dataset' | 'hardware';

export interface VitalData {
  patient_id: string;
  device_id: string;
  timestamp: string;
  heart_rate: number;
  spo2: number;
  respiratory_rate: number;
  ppg_samples: number[];
  signal_quality: number;
  source: VitalSource;
}

// Fixed to match backend: NORMAL | WATCH | HIGH_RISK
export type RiskLevel = 'NORMAL' | 'WATCH' | 'HIGH_RISK';

export interface RiskAnalysisResult {
  risk_score: number;
  risk_level: RiskLevel;
  confidence: number;
  contributing_factors: string[];
  anomalies: string[];
  recommendations: string[];  // Contains the formatted "✓ stable" / "⚠ issue" strings
  hrv_metrics?: {
    mean_rr?: number;
    sdnn?: number;
    rmssd?: number;
  };
  signal_sqi: number;
}

// Fixed to match backend: INFO | WATCH | HIGH
export interface ClinicalAlert {
  id: number;
  type: string;
  severity: 'INFO' | 'WATCH' | 'HIGH';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

export interface TelemetryPacket {
  type: 'VITAL_UPDATE';
  vital: VitalData;
  risk: RiskAnalysisResult;
  alerts: ClinicalAlert[];
}

export interface SimulatorStatus {
  running: boolean;
  scenario: string;
  patient_id: string;
  tick_rate_hz: number;
  available_scenarios?: string[];
}

export interface HistoricalVitalsResponse {
  patient_id: string;
  count: number;
  readings: (VitalData & { id: number; risk_score: number; risk_level: RiskLevel })[];
}
