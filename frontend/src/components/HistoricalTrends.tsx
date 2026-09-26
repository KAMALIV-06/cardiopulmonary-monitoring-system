import React, { useEffect, useState } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { fetchVitalHistory } from '../services/api';
import { History, RefreshCw } from 'lucide-react';

interface HistoricalTrendsProps {
  patientId: string;
  expanded?: boolean;
}

type TrendMetric = 'hr' | 'spo2' | 'rr' | 'risk';
const METRICS: Record<TrendMetric, { label: string; color: string; unit: string }> = {
  hr: { label: 'Heart rate', color: '#10b981', unit: 'bpm' },
  spo2: { label: 'SpO₂', color: '#06b6d4', unit: '%' },
  rr: { label: 'Respiratory rate', color: '#8b5cf6', unit: '/min' },
  risk: { label: 'Risk score', color: '#f59e0b', unit: '/100' },
};

export const HistoricalTrends: React.FC<HistoricalTrendsProps> = ({ patientId, expanded = false }) => {
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [windowMinutes, setWindowMinutes] = useState(5);
  const [metric, setMetric] = useState<TrendMetric>('hr');

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const records = await fetchVitalHistory(patientId, Math.min(10000, windowMinutes * 120), windowMinutes);
      const formatted = records.map((r: any, idx: number) => ({
        index: idx,
        time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        hr: r.heart_rate,
        spo2: r.spo2,
        rr: r.respiratory_rate,
        risk: r.risk_score,
        source: r.source,
      }));
      setData(formatted);
    } catch (e) {
      console.error('Failed to load vital history:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
    const interval = setInterval(loadHistory, 8000);
    return () => clearInterval(interval);
  }, [patientId, windowMinutes]);

  return (
    <div className={`p-6 rounded-2xl border border-slate-800 bg-[#0e1626] shadow-xl ${expanded ? 'min-h-[30rem]' : ''}`}>
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-blue-400">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">
              {expanded ? 'Historical Trends' : 'Recent Trends'}
            </h3>
            <p className="text-xs text-slate-400">Historical multi-parameter readings from the backend</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {[5, 15, 30, 60, 180, 1440, 10080].map(minutes => <button key={minutes} onClick={() => setWindowMinutes(minutes)} className={`rounded-lg border px-2.5 py-1.5 text-xs ${windowMinutes === minutes ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-300' : 'border-slate-800 text-slate-400'}`}>{minutes < 60 ? `${minutes}m` : minutes === 60 ? '1h' : minutes === 180 ? '3h' : minutes === 1440 ? '24h' : '7d'}</button>)}
          <button onClick={loadHistory} disabled={isLoading} className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition disabled:opacity-50"><RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} /></button>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">{(Object.keys(METRICS) as TrendMetric[]).map(key => <button key={key} onClick={() => setMetric(key)} className={`rounded-lg border px-3 py-1.5 text-xs ${metric === key ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-200' : 'border-slate-800 text-slate-400'}`}>{METRICS[key].label}</button>)}</div>
        <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-400">{[...new Set(data.map(point => point.source))].map(source => <span key={source} className="rounded-full border border-slate-700 px-2 py-1">{source === 'hardware' ? 'LIVE HARDWARE' : source === 'simulator' ? 'SIMULATOR' : 'DATASET REPLAY'}</span>)}</div>
      </div>

      <div className={`${expanded ? 'h-80' : 'h-60'} w-full`}>
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-500">
            Collecting historical readings from telemetry stream...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis domain={metric === 'spo2' ? [80, 100] : metric === 'risk' ? [0, 100] : metric === 'rr' ? [0, 40] : [30, 180]} stroke="#64748b" tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '11px' }}
                itemStyle={{ padding: 0 }}
                formatter={(value: number) => [`${Number(value).toFixed(1)} ${METRICS[metric].unit}`, METRICS[metric].label]}
                labelFormatter={(label, payload) => payload?.[0]?.payload ? `${label} · ${payload[0].payload.source === 'hardware' ? 'LIVE HARDWARE' : payload[0].payload.source === 'simulator' ? 'SIMULATOR' : 'DATASET REPLAY'}` : label}
              />
              <Line type="monotone" dataKey={metric} name={METRICS[metric].label} stroke={METRICS[metric].color} strokeWidth={2} dot={false} isAnimationActive={false} connectNulls />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <p className="mt-3 border-t border-slate-800/60 pt-3 text-center text-[11px] text-slate-500">{METRICS[metric].label}{metric === 'rr' ? ' · hardware values are PPG-derived estimates' : ''} · {windowMinutes}-minute view · browser-local time</p>
    </div>
  );
};
