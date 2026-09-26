import React, { useState, useEffect } from 'react';
import { AlertCircle, Bell, BellOff, CheckCircle2, X } from 'lucide-react';
import { ClinicalAlert } from '../types/vitals';
import { acknowledgeAlert } from '../services/api';

interface AlertBannerProps {
  alerts: ClinicalAlert[];
  onDismiss: (id: number) => void;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ alerts, onDismiss }) => {
  const [audioEnabled, setAudioEnabled] = useState(false);

  // Play synthetic medical monitor alarm chime for critical alerts
  useEffect(() => {
    if (!audioEnabled || alerts.length === 0) return;
    const hasCritical = alerts.some(a => a.severity === 'HIGH' && !a.acknowledged);
    if (!hasCritical) return;

    try {
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, ctx.currentTime); // 880 Hz beep
      osc.frequency.setValueAtTime(440, ctx.currentTime + 0.1);

      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.3);
    } catch (e) {
      // Audio playback restrictions handled
    }
  }, [alerts, audioEnabled]);

  if (alerts.length === 0) return null;

  const topAlert = alerts[0];

  const handleAcknowledge = async (id: number) => {
    await acknowledgeAlert(id);
    onDismiss(id);
  };

  return (
    <div className={`mb-6 p-4 rounded-2xl border transition-all shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${
      topAlert.severity === 'HIGH'
        ? 'bg-rose-950/40 border-rose-500/80 text-rose-200'
        : 'bg-amber-950/30 border-amber-500/60 text-amber-200'
    }`}>
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-xl shrink-0 ${
          topAlert.severity === 'HIGH' ? 'bg-rose-500/20 text-rose-400 animate-pulse' : 'bg-amber-500/20 text-amber-400'
        }`}>
          <AlertCircle className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700">
              {topAlert.severity} ALERT
            </span>
            <span className="text-xs text-slate-400 font-mono">
              {new Date(topAlert.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <p className="text-sm font-semibold text-white mt-1">
            {topAlert.message}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
        <button
          onClick={() => setAudioEnabled(!audioEnabled)}
          title={audioEnabled ? "Mute audio alarms" : "Enable sound alarm"}
          className={`p-2 rounded-xl border text-xs flex items-center gap-1.5 transition ${
            audioEnabled
              ? 'bg-slate-900 border-emerald-500/40 text-emerald-400'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
          }`}
        >
          {audioEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
          <span className="hidden md:inline">{audioEnabled ? 'Sound ON' : 'Muted'}</span>
        </button>

        <button
          onClick={() => handleAcknowledge(topAlert.id)}
          className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-white flex items-center gap-1.5 transition shadow"
        >
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Acknowledge</span>
        </button>

        <button
          onClick={() => onDismiss(topAlert.id)}
          className="p-2 rounded-xl bg-slate-900/60 hover:bg-slate-900 text-slate-400 hover:text-white transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
