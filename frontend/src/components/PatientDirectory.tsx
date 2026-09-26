import React, { useEffect, useState } from 'react';
import { Activity, ChevronRight, Users } from 'lucide-react';
import { fetchLatestVital, fetchPatients } from '../services/api';
import type { Patient } from '../types/patient';
import type { VitalData } from '../types/vitals';

type Latest = VitalData & { risk_level: string; risk_score: number };

export const PatientDirectory: React.FC<{
  selectedPatientId: string;
  onSelect: (patientId: string) => void;
}> = ({ selectedPatientId, onSelect }) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [latest, setLatest] = useState<Record<string, Latest | null>>({});
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    fetchPatients().then(rows => { if (active) setPatients(rows); })
      .catch(() => setError('Patient list is unavailable. Check the backend connection.'));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!patients.length) return;
    let active = true;
    const refresh = async () => {
      const vitals = await Promise.all(patients.map(async patient => {
        try { return [patient.id, await fetchLatestVital(patient.id)] as const; }
        catch { return [patient.id, null] as const; }
      }));
      if (active) setLatest(Object.fromEntries(vitals));
    };
    void refresh();
    const timer = window.setInterval(refresh, 15000);
    return () => { active = false; window.clearInterval(timer); };
  }, [patients]);

  return <section className="space-y-5">
    <header>
      <div className="flex items-center gap-2 text-cyan-300"><Users className="h-5 w-5" /><h2 className="text-xl font-bold text-white">Patients</h2></div>
      <p className="mt-1 text-sm text-slate-400">Care team roster with latest reading and monitoring source.</p>
    </header>
    {error && <p role="alert" className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">{error}</p>}
    <div className="overflow-hidden rounded-2xl border border-slate-800 bg-[#0e1626]">
      <div className="grid grid-cols-[1.5fr_0.7fr_0.8fr_0.8fr_1fr_auto] gap-3 border-b border-slate-800 px-5 py-3 text-[10px] font-semibold uppercase tracking-widest text-slate-500 max-md:hidden">
        <span>Patient</span><span>Age</span><span>Status</span><span>Risk</span><span>Source · device · last update</span><span />
      </div>
      {patients.map(patient => {
        const vital = latest[patient.id];
        const isSelected = patient.id === selectedPatientId;
        return <button key={patient.id} onClick={() => onSelect(patient.id)} className={`grid w-full grid-cols-1 gap-2 border-b border-slate-800/70 px-5 py-4 text-left transition hover:bg-slate-800/40 md:grid-cols-[1.5fr_0.7fr_0.8fr_0.8fr_1fr_auto] md:items-center ${isSelected ? 'bg-cyan-500/5' : ''}`}>
          <span><span className="block font-semibold text-white">{patient.name}</span><span className="mt-0.5 block font-mono text-xs text-slate-500">{patient.id} · {patient.medical_record_number ?? 'MRN not recorded'}</span></span>
          <span className="text-sm text-slate-300 md:before:hidden before:mr-2 before:text-xs before:text-slate-500 before:content-['Age']">{patient.age}</span>
          <span className="text-sm capitalize text-slate-300">{patient.monitoring_status}</span>
          <span className={`text-sm font-semibold ${vital?.risk_level === 'HIGH_RISK' ? 'text-rose-300' : vital?.risk_level === 'WATCH' ? 'text-amber-300' : 'text-emerald-300'}`}>{vital ? vital.risk_level.replace('_', ' ') : 'No reading'}</span>
          <span className="flex items-start gap-2 text-sm text-slate-300"><Activity className="mt-0.5 h-4 w-4 shrink-0 text-cyan-400" /><span>{vital ? <>{vital.source === 'hardware' ? 'Hardware' : vital.source === 'simulator' ? 'Simulator' : 'Dataset replay'} · {vital.device_id}<small className="mt-1 block text-[10px] text-slate-500">{new Date(vital.timestamp).toLocaleString()} · {Date.now() - new Date(vital.timestamp).getTime() < 15000 ? 'Recent' : 'Last reading'}</small></> : 'Waiting for data'}</span></span>
          <ChevronRight className="hidden h-4 w-4 text-slate-500 md:block" />
        </button>;
      })}
      {!patients.length && !error && <p className="p-6 text-sm text-slate-400">Loading patients… Seed the synthetic cohort if this is a new database.</p>}
    </div>
    <p className="text-xs text-slate-500">Values shown here are monitoring indicators for care-team review, not diagnoses. Synthetic profiles are marked in their records.</p>
  </section>;
};
