import React, { useEffect, useState } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { fetchVitalHistory } from '../services/api';
import { History, RefreshCw } from 'lucide-react';

interface HistoricalTrendsProps {
  patientId: string;
  expanded?: boolean;
}

export const HistoricalTrends: React.FC<HistoricalTrendsProps> = ({ patientId }) => {
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [windowMinutes, setWindowMinutes] = useState(5);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const records = await fetchVitalHistory(patientId, windowMinutes * 120, windowMinutes);
      const formatted = records.map((r: any, idx: number) => ({
        index: idx,
        time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        hr: r.heart_rate,
        spo2: r.spo2,
        rr: r.respiratory_rate,
        risk: r.risk_score
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
    <div className="p-6 rounded-2xl border border-slate-800 bg-[#0e1626] shadow-xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-blue-400">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">
              Historical Physiological Trends
            </h3>
            <p className="text-xs text-slate-400">Historical multi-parameter readings from the backend</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {[5, 15, 30, 60].map(minutes => <button key={minutes} onClick={() => setWindowMinutes(minutes)} className={`rounded-lg border px-2.5 py-1.5 text-xs ${windowMinutes === minutes ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-300' : 'border-slate-800 text-slate-400'}`}>{minutes}m</button>)}
          <button onClick={loadHistory} disabled={isLoading} className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition disabled:opacity-50"><RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} /></button>
        </div>
      </div>

      <div className="h-60 w-full">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-500">
            Collecting historical readings from telemetry stream...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis domain={[30, 160]} stroke="#64748b" tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '11px' }}
                itemStyle={{ padding: 0 }}
              />
              <Line type="monotone" dataKey="hr" name="Heart Rate (bpm)" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
              <Line type="monotone" dataKey="spo2" name="SpO2 (%)" stroke="#06b6d4" strokeWidth={2} dot={false} isAnimationActive={false} />
              <Line type="monotone" dataKey="rr" name="Resp Rate (estimate/min)" stroke="#8b5cf6" strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="flex items-center justify-center gap-6 mt-3 pt-3 border-t border-slate-800/60 text-xs font-medium">
        <div className="flex items-center gap-2 text-emerald-400">
          <span className="w-3 h-0.5 bg-emerald-400 rounded-full" />
          <span>Heart Rate</span>
        </div>
        <div className="flex items-center gap-2 text-cyan-400">
          <span className="w-3 h-0.5 bg-cyan-400 rounded-full" />
          <span>SpO2 Oxygen</span>
        </div>
        <div className="flex items-center gap-2 text-purple-400">
          <span className="w-3 h-0.5 bg-purple-400 rounded-full" />
          <span>Resp Rate estimate</span>
        </div>
      </div>
    </div>
  );
};
