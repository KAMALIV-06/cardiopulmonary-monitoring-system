import React from 'react';
import { Heart, Wind, Droplets, ArrowUpRight, ArrowDownRight, AlertTriangle } from 'lucide-react';

interface VitalCardProps {
  type: 'hr' | 'spo2' | 'rr';
  value: number;
  unit: string;
  label: string;
  isWarning?: boolean;
  isCritical?: boolean;
  statusText?: string;
  normalRange: string;
}

export const VitalCard: React.FC<VitalCardProps> = ({
  type,
  value,
  unit,
  label,
  isWarning = false,
  isCritical = false,
  statusText = 'Normal',
  normalRange,
}) => {
  // Theme styling based on vital type
  const theme = {
    hr: {
      icon: Heart,
      accent: 'text-emerald-400',
      border: isCritical ? 'border-rose-500/80 bg-rose-950/20' : isWarning ? 'border-amber-500/80 bg-amber-950/20' : 'border-emerald-500/20 bg-emerald-950/10',
      glow: isCritical ? 'shadow-rose-500/10' : isWarning ? 'shadow-amber-500/10' : 'shadow-emerald-500/5',
      badge: isCritical ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' : isWarning ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      pulse: true
    },
    spo2: {
      icon: Droplets,
      accent: 'text-cyan-400',
      border: isCritical ? 'border-rose-500/80 bg-rose-950/20' : isWarning ? 'border-amber-500/80 bg-amber-950/20' : 'border-cyan-500/20 bg-cyan-950/10',
      glow: isCritical ? 'shadow-rose-500/10' : isWarning ? 'shadow-amber-500/10' : 'shadow-cyan-500/5',
      badge: isCritical ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' : isWarning ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
      pulse: false
    },
    rr: {
      icon: Wind,
      accent: 'text-purple-400',
      border: isCritical ? 'border-rose-500/80 bg-rose-950/20' : isWarning ? 'border-amber-500/80 bg-amber-950/20' : 'border-purple-500/20 bg-purple-950/10',
      glow: isCritical ? 'shadow-rose-500/10' : isWarning ? 'shadow-amber-500/10' : 'shadow-purple-500/5',
      badge: isCritical ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' : isWarning ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      pulse: false
    }
  }[type];

  const Icon = theme.icon;

  return (
    <div className={`relative p-5 rounded-2xl border ${theme.border} bg-[#0e1626] shadow-xl ${theme.glow} flex flex-col justify-between transition-all duration-300`}>
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-xl bg-slate-900/80 border border-slate-800 ${theme.accent}`}>
            <Icon className={`w-5 h-5 ${theme.pulse && value > 0 ? 'animate-heart-pulse text-emerald-400' : ''}`} />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              {label}
            </span>
            <p className="text-[11px] text-slate-500 font-mono">Norm: {normalRange}</p>
          </div>
        </div>

        {/* Status Badge */}
        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${theme.badge} flex items-center gap-1`}>
          {(isWarning || isCritical) && <AlertTriangle className="w-3 h-3" />}
          {statusText}
        </span>
      </div>

      {/* Main Vital Reading Value */}
      <div className="my-4 flex items-baseline gap-2">
        <span className={`text-4xl lg:text-5xl font-mono font-extrabold tracking-tight ${
          isCritical ? 'text-rose-400' : isWarning ? 'text-amber-400' : 'text-white'
        }`}>
          {value > 0 ? value.toFixed(1) : '--'}
        </span>
        <span className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
          {unit}
        </span>
      </div>

      {/* Bottom Subtext */}
      <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
        <span>Continuous Real-time</span>
        <span className="font-mono text-[11px] text-slate-500">Live Window</span>
      </div>
    </div>
  );
};
