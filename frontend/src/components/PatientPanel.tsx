import React, { useEffect, useState } from 'react';
import { VitalData, RiskAnalysisResult } from '../types/vitals';

interface Patient { id: string; name: string; age: number; gender: string; }
export const PatientPanel: React.FC<{ patientId: string; vital: VitalData | null; risk: RiskAnalysisResult | null; isConnected: boolean; monitoringStart: string | null }> = ({ patientId, vital, risk, isConnected, monitoringStart }) => {
  const [patient, setPatient] = useState<Patient | null>(null);
  useEffect(() => { fetch(`http://localhost:8000/api/v1/patients/${patientId}`).then(r => r.ok ? r.json() : null).then(setPatient).catch(() => setPatient(null)); }, [patientId]);
  return <section className="rounded-2xl border border-slate-800 bg-[#0e1626] p-6">
    <h2 className="text-lg font-bold text-white">Patient</h2><p className="mb-5 text-sm text-slate-400">Demo patient record and current monitoring state.</p>
    <dl className="grid gap-4 sm:grid-cols-2 text-sm">
      <div><dt className="text-slate-500">Patient ID</dt><dd className="mt-1 text-white">{patientId}</dd></div>
      <div><dt className="text-slate-500">Patient</dt><dd className="mt-1 text-white">{patient?.name ?? 'Loading patient…'}</dd></div>
      <div><dt className="text-slate-500">Device</dt><dd className="mt-1 text-white">{vital?.device_id ?? 'Waiting for telemetry'}</dd></div>
      <div><dt className="text-slate-500">Monitoring since</dt><dd className="mt-1 text-white">{monitoringStart ? new Date(monitoringStart).toLocaleString() : 'Awaiting first reading'}</dd></div>
      <div><dt className="text-slate-500">Connection</dt><dd className="mt-1 text-white">{isConnected ? 'Live' : 'Reconnecting'}</dd></div>
      <div><dt className="text-slate-500">Current risk</dt><dd className="mt-1 text-white">{risk ? `${risk.risk_level} · ${risk.risk_score}/100` : 'Waiting for assessment'}</dd></div>
      <div><dt className="text-slate-500">Last update</dt><dd className="mt-1 text-white">{vital ? new Date(vital.timestamp).toLocaleString() : 'No data yet'}</dd></div>
    </dl>
  </section>;
};
