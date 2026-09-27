import React, { useEffect, useState } from 'react';
import { Cpu, Radio, Layers } from 'lucide-react';
import { VitalData } from '../types/vitals';

interface HardwareStatusBadgeProps {
  vital: VitalData | null;
}

export const HardwareStatusBadge: React.FC<HardwareStatusBadgeProps> = ({ vital }) => {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);
  const source = vital?.source;
  const deviceId = vital?.device_id;
  const hardwareFresh = source === 'hardware' && !!vital && now - new Date(vital.timestamp).getTime() < 15000;
  const sourceLabel = source === 'hardware' ? hardwareFresh ? 'LIVE HARDWARE · ESP8266 + MAX30102' : 'HARDWARE · LAST PACKET STALE' : source === 'simulator' ? 'SIMULATOR' : source === 'dataset' ? 'DATASET REPLAY' : 'WAITING';

  return (
    <div className="p-4 rounded-2xl border border-slate-800 bg-[#0e1626] shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      {/* Active Device & Ingestion Info */}
      <div className="flex items-center gap-3">
        <div className={`p-2.5 rounded-xl border ${
          source === 'hardware'
            ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
            : source === 'dataset'
            ? 'bg-purple-500/10 border-purple-500/30 text-purple-400'
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
        }`}>
          {source === 'hardware' ? <Cpu className="w-5 h-5" /> : <Radio className="w-5 h-5" />}
        </div>

        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase font-semibold tracking-wider text-slate-400">
              Most Recent Source:
            </span>
            <span className={`text-xs font-mono font-bold uppercase px-2 py-0.5 rounded-md border ${
              source === 'hardware'
                ? 'bg-amber-950/40 text-amber-400 border-amber-800/60'
                : source === 'dataset'
                ? 'bg-purple-950/40 text-purple-400 border-purple-800/60'
                : 'bg-emerald-950/40 text-emerald-400 border-emerald-800/60'
            }`}>
              {sourceLabel}
            </span>
          </div>
          <p className="text-xs font-mono text-slate-400 mt-0.5">
            Node ID: <span className="text-white font-semibold">{deviceId ?? 'Waiting for telemetry'}</span> • Protocol: Normalized VitalData
          </p>
        </div>
      </div>

      {/* Hardware Independence Note & SQI */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
          <Layers className="w-3.5 h-3.5 text-blue-400" />
          <span>Hardware Abstraction Layer Active</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <span className="text-slate-400">Signal quality:</span>
          <span className="font-mono font-bold text-slate-300">Not available</span>
        </div>
      </div>
    </div>
  );
};
