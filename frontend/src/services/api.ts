import { VitalData, SimulatorStatus, ClinicalAlert } from '../types/vitals';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export async function fetchLatestVital(patientId: string = 'PATIENT-001') {
  const res = await fetch(`${API_BASE}/vitals/${patientId}/latest`);
  if (!res.ok) return null;
  return res.json();
}

export async function fetchVitalHistory(patientId: string = 'PATIENT-001', limit: number = 60, windowMinutes?: number) {
  const range = windowMinutes ? `&window_minutes=${windowMinutes}` : '';
  const res = await fetch(`${API_BASE}/vitals/${patientId}/history?limit=${limit}${range}`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.readings || [];
}

export async function fetchAlerts(patientId: string = 'PATIENT-001'): Promise<ClinicalAlert[]> {
  const res = await fetch(`${API_BASE}/alerts/${patientId}`);
  if (!res.ok) return [];
  return res.json();
}

export async function acknowledgeAlert(alertId: number): Promise<ClinicalAlert | null> {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
    method: 'POST'
  });
  if (!res.ok) return null;
  return res.json();
}

export async function fetchSimulatorStatus(): Promise<SimulatorStatus> {
  const res = await fetch(`${API_BASE}/simulator/status`);
  if (!res.ok) throw new Error('Failed to fetch simulator status');
  return res.json();
}

export async function startSimulator() {
  const res = await fetch(`${API_BASE}/simulator/start`, { method: 'POST' });
  return res.json();
}

export async function stopSimulator() {
  const res = await fetch(`${API_BASE}/simulator/stop`, { method: 'POST' });
  return res.json();
}

export async function setSimulatorScenario(scenario: string, patientId: string = 'PATIENT-001') {
  const res = await fetch(`${API_BASE}/simulator/scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario, patient_id: patientId })
  });
  return res.json();
}

export async function simulateHardwareTransmission(payload: {
  device_id: string;
  patient_id: string;
  ppg_samples: number[];
  signal_quality: number;
  heart_rate: number;
  spo2: number;
}) {
  const res = await fetch(`${API_BASE}/ingest/hardware`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}
