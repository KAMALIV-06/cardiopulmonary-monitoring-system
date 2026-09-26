import React, { useState } from 'react';
import { X, Play, Square, Activity, AlertTriangle, CheckCircle, Zap } from 'lucide-react';
import { setSimulatorScenario, startSimulator, stopSimulator } from '../services/api';

interface SimulatorControlModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentScenario: string;
  onScenarioChange?: (newScenario: string) => void;
}

const SCENARIOS = [
  {
    id: 'normal',
    title: 'Normal Sinus Rhythm',
    badge: 'Healthy Baseline',
    badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    description: 'Resting healthy adult. Regular rhythm, SpO2 > 98%, HR ~72 bpm, RR 14.',
    metrics: 'HR 72 | SpO2 98% | RR 14'
  },
  {
    id: 'hypoxemia',
    title: 'Acute Hypoxemic Distress',
    badge: 'Critical Pulmonary',
    badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
    description: 'Sudden desaturation (COPD / Pneumonia). Rapid shallow tachypnea. SpO2 drops below 90%.',
    metrics: 'HR 112 | SpO2 86% | RR 28'
  },
  {
    id: 'tachycardia',
    title: 'Severe Tachycardia / Cardiac Stress',
    badge: 'High Cardiac Risk',
    badgeColor: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
    description: 'Excessive heart rate exceeding 140 bpm — elevated myocardial oxygen demand.',
    metrics: 'HR 148 | SpO2 94% | RR 22'
  },
  {
    id: 'bradycardia',
    title: 'Severe Sinus Bradycardia',
    badge: 'Conduction Block',
    badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    description: 'Pathologically low heart rate (< 40 bpm) with compensatory deep breathing.',
    metrics: 'HR 36 | SpO2 93% | RR 10'
  },
  {
    id: 'tachypnea',
    title: 'Isolated Tachypnea',
    badge: 'Respiratory Fatigue',
    badgeColor: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
    description: 'Rapid shallow breathing without primary hypoxemia — early respiratory fatigue or anxiety.',
    metrics: 'HR 88 | SpO2 95% | RR 30'
  },
  {
    id: 'arrhythmia',
    title: 'Irregular Pulse',
    badge: 'Pulse Variability',
    badgeColor: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    description: 'Synthetic irregular pulse intervals and waveform variability for a demo scenario.',
    metrics: 'HR 84 | SpO2 95% | Irregular RR'
  },
  {
    id: 'sensor_disconnect',
    title: 'Optical Sensor Disconnect',
    badge: 'Sensor Unavailable',
    badgeColor: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
    description: 'Electrode detached from skin — simulates 50/60Hz ambient interference and critical SQI.',
    metrics: 'Flatline / 60Hz Hum • SQI < 0.1'
  }
];


export const SimulatorControlModal: React.FC<SimulatorControlModalProps> = ({
  isOpen,
  onClose,
  currentScenario,
  onScenarioChange
}) => {
  const [selected, setSelected] = useState(currentScenario);
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSelectScenario = async (id: string) => {
    setIsLoading(true);
    try {
      await setSimulatorScenario(id, 'PATIENT-001');
      setSelected(id);
      if (onScenarioChange) onScenarioChange(id);
    } catch (e) {
      console.error('Failed to change scenario:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStart = async () => {
    await startSimulator();
  };

  const handleStop = async () => {
    await stopSimulator();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-2xl rounded-3xl border border-slate-800 bg-[#0c121e] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                Physiological Scenario Simulator
              </h2>
              <p className="text-xs text-slate-400">
                Test and demonstrate early risk detection protocols in real time
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scenarios Grid */}
        <div className="p-6 overflow-y-auto space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {SCENARIOS.map((sc) => {
              const isActive = selected === sc.id;
              return (
                <div
                  key={sc.id}
                  onClick={() => handleSelectScenario(sc.id)}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                    isActive
                      ? 'border-emerald-500 bg-emerald-950/20 shadow-lg shadow-emerald-500/10'
                      : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        {sc.title}
                        {isActive && <CheckCircle className="w-4 h-4 text-emerald-400" />}
                      </h4>
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${sc.badgeColor}`}>
                        {sc.badge}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed mb-3">
                      {sc.description}
                    </p>
                  </div>
                  <div className="pt-2 border-t border-slate-800/80 text-[11px] font-mono text-emerald-400/90 font-semibold">
                    {sc.metrics}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Modal Footer Controls */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={handleStart}
              className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow transition"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Resume Stream</span>
            </button>
            <button
              onClick={handleStop}
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>Pause Stream</span>
            </button>
          </div>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-semibold transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
