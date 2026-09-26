import React, { useEffect, useState } from 'react';
import { acknowledgeAlert, fetchAlerts } from '../services/api';
import { ClinicalAlert } from '../types/vitals';

export const AlertsPanel: React.FC<{ patientId: string; liveAlerts: ClinicalAlert[] }> = ({ patientId, liveAlerts }) => {
  const [alerts, setAlerts] = useState<ClinicalAlert[]>([]);
  const refresh = async () => setAlerts(await fetchAlerts(patientId));
  useEffect(() => { void refresh(); const timer = setInterval(refresh, 5000); return () => clearInterval(timer); }, [patientId]);
  useEffect(() => { if (liveAlerts.length) void refresh(); }, [liveAlerts]);
  const acknowledge = async (id: number) => { await acknowledgeAlert(id); await refresh(); };
  return <section className="rounded-2xl border border-slate-800 bg-[#0e1626] p-6">
    <h2 className="text-lg font-bold text-white">Alerts</h2>
    <p className="mb-5 text-sm text-slate-400">Current and recent alerts loaded from the backend.</p>
    {alerts.length === 0 ? <p className="text-sm text-slate-400">No active alerts.</p> : <div className="space-y-3">
      {alerts.map(alert => <article key={alert.id} className="flex items-center justify-between gap-4 rounded-xl border border-slate-800 p-4">
        <div><div className="text-xs font-semibold uppercase text-amber-300">{alert.severity} · {alert.type}</div><div className="mt-1 text-sm text-white">{alert.message}</div><time className="text-xs text-slate-500">{new Date(alert.timestamp).toLocaleString()}</time></div>
        {alert.acknowledged ? <span className="text-xs text-slate-500">Acknowledged</span> : <button onClick={() => void acknowledge(alert.id)} className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-white">Acknowledge</button>}
      </article>)}
    </div>}
  </section>;
};
