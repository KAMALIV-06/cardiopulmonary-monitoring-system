import React, { useEffect, useState } from 'react';
import { ClipboardList, Pill, ShieldAlert, TestTube2, UserRound } from 'lucide-react';
import { fetchPatientProfile } from '../services/api';
import type { PatientProfile as Profile } from '../types/patient';

const dateLabel = (value?: string | null) => value ? new Date(value).toLocaleString() : 'Not recorded';
const Panel: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode }> = ({ title, icon, children }) => <section className="rounded-2xl border border-slate-800 bg-[#0e1626] p-5">
  <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-white">{icon}{title}</h3>{children}
</section>;

export const ClinicalProfile: React.FC<{ patientId: string }> = ({ patientId }) => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    setProfile(null); setError('');
    fetchPatientProfile(patientId).then(value => { if (active) setProfile(value); })
      .catch(() => { if (active) setError('Clinical profile could not be loaded.'); });
    return () => { active = false; };
  }, [patientId]);

  if (error) return <p role="alert" className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">{error}</p>;
  if (!profile) return <p className="p-5 text-sm text-slate-400">Loading clinical profile…</p>;
  const patient = profile.patient;
  const demo = patient.demo_data;

  return <div className="space-y-5">
    <header className="flex flex-wrap items-start justify-between gap-3">
      <div><div className="flex items-center gap-2"><UserRound className="h-5 w-5 text-cyan-300"/><h2 className="text-xl font-bold text-white">Clinical Profile</h2></div>
        <p className="mt-1 text-sm text-slate-400">Patient background and recorded context for care-team review.</p></div>
      <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${demo ? 'border-amber-500/30 bg-amber-500/10 text-amber-200' : 'border-slate-700 text-slate-300'}`}>{demo ? 'DEMO / SYNTHETIC DATA' : 'CLINICAL RECORD'}</span>
    </header>

    <Panel title="Patient information" icon={<UserRound className="h-4 w-4 text-cyan-300"/>}>
      <div className="grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
        <Info label="Name" value={patient.name}/><Info label="Patient ID" value={patient.id}/><Info label="Age / gender" value={`${patient.age} · ${patient.gender}`}/>
        <Info label="Medical record number" value={patient.medical_record_number || 'Not recorded'}/><Info label="Monitoring status" value={patient.monitoring_status}/>
        <Info label="Height / weight" value={`${patient.height_cm ?? '—'} cm · ${patient.weight_kg ?? '—'} kg`}/>
        <Info label="Baseline notes" value={patient.baseline_notes || 'No notes recorded'}/>
      </div>
    </Panel>

    <div className="grid gap-5 lg:grid-cols-2">
      <Panel title="Medical history & events" icon={<ClipboardList className="h-4 w-4 text-cyan-300"/>}>
        <ul className="space-y-3 text-sm">
          {profile.medical_history.map(item => <li key={item.id} className="border-b border-slate-800 pb-3 last:border-0"><div className="flex justify-between gap-3 text-white"><span>{item.condition_name}</span><span className="text-xs capitalize text-slate-400">{item.status}</span></div><p className="mt-1 text-xs text-slate-500">{item.diagnosis_date || 'Date not recorded'} · {item.notes}</p></li>)}
          {profile.events.map(event => <li key={`event-${event.id}`} className="border-b border-slate-800 pb-3 last:border-0"><div className="text-white">{event.summary}</div><p className="mt-1 text-xs text-slate-500">{event.event_type} · {dateLabel(event.occurred_at)} · {event.source}</p></li>)}
          {!profile.medical_history.length && !profile.events.length && <Empty/>}
        </ul>
      </Panel>
      <Panel title="Medications" icon={<Pill className="h-4 w-4 text-cyan-300"/>}>
        <ul className="space-y-3 text-sm">{profile.medications.map(item => <li key={item.id} className="border-b border-slate-800 pb-3 last:border-0"><div className="text-white">{item.medication_name} <span className="text-slate-400">· {item.dosage}</span></div><p className="mt-1 text-xs text-slate-500">{item.frequency} · {item.start_date || 'Start date not recorded'}{item.end_date ? ` – ${item.end_date}` : ''}</p></li>)}{!profile.medications.length && <Empty/>}</ul>
      </Panel>
      <Panel title="Allergies" icon={<ShieldAlert className="h-4 w-4 text-amber-300"/>}>
        <ul className="space-y-3 text-sm">{profile.allergies.map(item => <li key={item.id} className="flex justify-between gap-3 border-b border-slate-800 pb-3 last:border-0"><span className="text-white">{item.allergen}<small className="mt-1 block text-slate-500">Reaction: {item.reaction}</small></span><span className="text-xs uppercase text-amber-200">{item.severity}</span></li>)}{!profile.allergies.length && <Empty/>}</ul>
      </Panel>
      <Panel title="Recent clinical measurements" icon={<ClipboardList className="h-4 w-4 text-cyan-300"/>}>
        <ul className="space-y-3 text-sm">{profile.clinical_measurements.map(item => <li key={item.id} className="flex items-start justify-between gap-3 border-b border-slate-800 pb-3 last:border-0"><span className="text-slate-300">{item.measurement_type}<small className="mt-1 block text-slate-500">{item.source} · {dateLabel(item.measured_at)}</small></span><strong className="whitespace-nowrap text-white">{item.value} {item.unit}</strong></li>)}{!profile.clinical_measurements.length && <Empty/>}</ul>
      </Panel>
      <Panel title="Laboratory results" icon={<TestTube2 className="h-4 w-4 text-cyan-300"/>}>
        <ul className="space-y-3 text-sm">{profile.lab_results.map(item => <li key={item.id} className="flex items-start justify-between gap-3 border-b border-slate-800 pb-3 last:border-0"><span className="text-slate-300">{item.test_name}<small className="mt-1 block text-slate-500">Ref: {item.reference_range || 'Not supplied'} · {dateLabel(item.measured_at)}</small></span><strong className="whitespace-nowrap text-white">{item.value} {item.unit}</strong></li>)}{!profile.lab_results.length && <Empty/>}</ul>
      </Panel>
    </div>
    <p className="text-xs text-slate-500">Clinical record values are separate from live sensor readings. {demo ? 'This profile contains synthetic demo data only.' : 'Source and recorded date are shown for each clinical item.'}</p>
  </div>;
};

const Info: React.FC<{label: string; value: string}> = ({label,value}) => <div><div className="text-xs text-slate-500">{label}</div><div className="mt-1 break-words text-white">{value}</div></div>;
const Empty = () => <li className="text-xs text-slate-500">No entries recorded.</li>;
