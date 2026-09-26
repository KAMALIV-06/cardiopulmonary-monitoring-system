import React, { useEffect, useState } from 'react';
import { fetchPatientProfile } from '../services/api';
import type { PatientProfile } from '../types/patient';
import type { VitalData, RiskAnalysisResult } from '../types/vitals';

interface PatientPanelProps {
  patientId: string;
  vital: VitalData | null;
  risk: RiskAnalysisResult | null;
  isConnected: boolean;
  monitoringStart: string | null;
}

export const PatientPanel: React.FC<PatientPanelProps> = ({ patientId, vital, risk, isConnected, monitoringStart }) => {
  const [profile, setProfile] = useState<PatientProfile | null>(null);
  useEffect(() => {
    let active = true;
    setProfile(null);
    fetchPatientProfile(patientId).then(result => { if (active) setProfile(result); }).catch(() => { if (active) setProfile(null); });
    return () => { active = false; };
  }, [patientId]);

  const patient = profile?.patient;
  const clinicalSnapshot = profile?.clinical_measurements.slice(0, 3) ?? [];
  return <section className="rounded-2xl border border-slate-800 bg-[#0e1626] p-5">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div><h2 className="text-base font-bold text-white">{patient?.name ?? 'Patient clinical context'}</h2><p className="mt-1 text-xs text-slate-400">{patientId} · {patient ? `${patient.age} · ${patient.gender}` : 'Loading profile'}</p></div>
      {patient?.demo_data && <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-[10px] font-bold text-amber-200">DEMO / SYNTHETIC DATA</span>}
    </div>
    <div className="mt-4 grid gap-4 text-sm sm:grid-cols-2 xl:grid-cols-4">
      <Context label="Medical history" value={profile?.medical_history.slice(0, 2).map(item => item.condition_name).join(' · ') || 'No profile entries'}/>
      <Context label="Medications" value={profile?.medications.slice(0, 2).map(item => `${item.medication_name} ${item.dosage}`).join(' · ') || 'No profile entries'}/>
      <Context label="Recent clinical data" value={clinicalSnapshot.map(item => `${item.measurement_type}: ${item.value} ${item.unit}`).join(' · ') || 'No clinical measurements'}/>
      <Context label="Allergies" value={profile?.allergies.slice(0, 2).map(item => `${item.allergen} (${item.severity})`).join(' · ') || 'No profile entries'}/>
    </div>
    <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 border-t border-slate-800 pt-3 text-[11px] text-slate-400">
      <span>MRN: {patient?.medical_record_number ?? 'Not recorded'}</span>
      <span>Risk: {risk ? `${risk.risk_level.replace('_', ' ')} · ${risk.risk_score.toFixed(1)}/100` : 'Awaiting analysis'}</span>
      <span>Device: {vital?.device_id ?? 'Waiting'}</span>
      <span>Source: {vital?.source === 'hardware' ? 'HARDWARE · ESP8266 + MAX30102' : vital?.source === 'simulator' ? 'SIMULATOR' : vital?.source === 'dataset' ? 'DATASET REPLAY' : 'Waiting'}</span>
      <span>WebSocket: {isConnected ? 'Connected' : 'Reconnecting'}</span>
      <span>Last update: {vital ? new Date(vital.timestamp).toLocaleString() : monitoringStart ? new Date(monitoringStart).toLocaleString() : 'No data'}</span>
    </div>
    {clinicalSnapshot[0] && <p className="mt-2 text-[10px] text-slate-500">Clinical record · last updated {new Date(clinicalSnapshot[0].measured_at).toLocaleString()}. Clinical information is separate from sensor data.</p>}
  </section>;
};

const Context: React.FC<{ label: string; value: string }> = ({ label, value }) => <div><p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{label}</p><p className="mt-1 text-xs leading-relaxed text-slate-200">{value}</p></div>;
