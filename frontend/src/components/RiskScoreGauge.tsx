import React from 'react';
import { ShieldCheck, ShieldAlert, AlertOctagon, Stethoscope } from 'lucide-react';
import { RiskAnalysisResult, RiskLevel } from '../types/vitals';

interface RiskScoreGaugeProps {
  risk: RiskAnalysisResult | null;
}

export const RiskScoreGauge: React.FC<RiskScoreGaugeProps> = ({ risk }) => {
  if (!risk) return <div className="p-6 rounded-2xl border border-slate-800 bg-[#0e1626] text-slate-400">Waiting for backend risk assessment…</div>;
  const score = risk.risk_score;
  const level = risk.risk_level;
  const anomalies = risk.anomalies;
  const recommendations = risk.recommendations;

  // Styling based on risk level
  const configurations: Record<RiskLevel, { color: string; bg: string; border: string; bar: string; icon: React.ElementType; badge: string }> = {
    NORMAL: {
      color: 'text-emerald-400',
      bg: 'bg-emerald-950/20',
      border: 'border-emerald-500/30',
      bar: 'bg-emerald-500',
      icon: ShieldCheck,
      badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
    },
    WATCH: {
      color: 'text-amber-400',
      bg: 'bg-amber-950/20',
      border: 'border-amber-500/30',
      bar: 'bg-amber-500',
      icon: ShieldAlert,
      badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30'
    },
    HIGH_RISK: {
      color: 'text-orange-400',
      bg: 'bg-orange-950/30',
      border: 'border-orange-500/50',
      bar: 'bg-orange-500',
      icon: AlertOctagon,
      badge: 'bg-orange-500/20 text-orange-300 border-orange-500/40'
    },
  };
  const config = configurations[level] ?? configurations.NORMAL;
  const Icon = config.icon;

  return (
    <div className={`p-6 rounded-2xl border ${config.border} bg-[#0e1626] shadow-2xl flex flex-col justify-between transition-all duration-300`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-xl bg-slate-900 border border-slate-800 ${config.color}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">
              Cardiopulmonary Early Warning
            </h3>
            <p className="text-xs text-slate-400">Transparent baseline risk indication · not a diagnosis</p>
          </div>
        </div>

        <span className={`text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full border ${config.badge}`}>
          {level} RISK
        </span>
      </div>

      {/* Main Score Bar & Value */}
      <div className="my-5">
        <div className="flex items-baseline justify-between mb-2">
          <span className="text-xs text-slate-400 font-medium">Compound Severity Score</span>
          <div className="flex items-baseline gap-1">
            <span className={`text-3xl font-mono font-black ${config.color}`}>
              {score.toFixed(1)}
            </span>
            <span className="text-xs text-slate-500 font-mono">/ 100</span>
          </div>
        </div>

        {/* Progress meter */}
        <div className="w-full h-3 rounded-full bg-slate-800 overflow-hidden p-0.5 border border-slate-700/50">
          <div
            className={`h-full rounded-full transition-all duration-500 ${config.bar}`}
            style={{ width: `${Math.max(4, Math.min(100, score))}%` }}
          />
        </div>
      </div>

      {/* Anomaly Detection List */}
      <div className="mb-4">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
          <span>Active Diagnostic Findings</span>
        </h4>
        <div className="space-y-1.5 max-h-28 overflow-y-auto pr-1">
          {anomalies.map((anomaly, idx) => (
            <div
              key={idx}
              className="text-xs px-3 py-2 rounded-lg bg-slate-900/90 border border-slate-800/80 text-slate-300 flex items-start gap-2"
            >
              <span className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${config.bar}`} />
              <span>{anomaly}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Clinical Guidance Recommendations */}
      <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-start gap-2.5">
        <Stethoscope className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
        <div className="text-xs text-slate-300">
          <span className="font-semibold text-white">Suggested Action: </span>
          {recommendations[0] || 'Continue routine telemetry.'}
        </div>
      </div>
    </div>
  );
};
