import React from 'react';
import { Activity, Radio, Cpu, Settings2, ShieldAlert } from 'lucide-react';
import { VitalSource } from '../types/vitals';

interface NavbarProps {
  isConnected: boolean;
  source?: VitalSource;
  patientId: string;
  onOpenSimulator: () => void;
  onOpenHardwareTest: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  isConnected,
  source,
  patientId,
  onOpenSimulator,
  onOpenHardwareTest,
}) => {
  return (
    <header className="border-b border-slate-800 bg-[#0c121e]/90 backdrop-blur sticky top-0 z-40 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Logo and Project Identity */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/5">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base lg:text-lg font-bold tracking-tight text-white">
                Cardiopulmonary Monitoring & Early Risk Detection
              </h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Imagine Cup 2026
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Hardware-independent telemetry & baseline early warning
            </p>
          </div>
        </div>

        {/* Status Indicators & Controls */}
        <div className="flex items-center gap-3 flex-wrap">
          {/* WebSocket Link Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 shadow-sm shadow-emerald-500' : 'bg-rose-500 animate-ping'}`} />
            <span className="text-slate-300 font-medium">
              {isConnected ? 'Telemetry Online' : 'Connecting...'}
            </span>
          </div>

          {/* Active Data Ingestion Source */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <Radio className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">Source:</span>
            <span className={`font-mono font-semibold uppercase ${
              source === 'hardware' ? 'text-amber-400' : source === 'dataset' ? 'text-purple-400' : 'text-emerald-400'
            }`}>
              [{source ?? 'waiting'}]
            </span>
          </div>

          {/* Patient Badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <span className="text-slate-400">Patient:</span>
            <span className="font-mono font-semibold text-white">{patientId}</span>
          </div>

          {/* Simulator Control Trigger */}
          <button
            onClick={onOpenSimulator}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs font-medium transition shadow-sm"
          >
            <Settings2 className="w-3.5 h-3.5" />
            <span>Scenario Simulator</span>
          </button>

          {/* MAX30102 Hardware Injection Trigger */}
          <button
            onClick={onOpenHardwareTest}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-medium transition shadow-sm"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Simulate MAX30102 Ingest</span>
          </button>
        </div>
      </div>
    </header>
  );
};
