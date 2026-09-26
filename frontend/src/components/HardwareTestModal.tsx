import React, { useState } from 'react';
import { X, Cpu, Send, CheckCircle2, AlertCircle } from 'lucide-react';
import { simulateHardwareTransmission } from '../services/api';

interface HardwareTestModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId: string;
}

export const HardwareTestModal: React.FC<HardwareTestModalProps> = ({
  isOpen,
  onClose,
  patientId
}) => {
  const [deviceId, setDeviceId] = useState('ESP8266-MAX30102-01');
  const [heartRate, setHeartRate] = useState(88);
  const [spo2, setSpo2] = useState(96.5);
  const [sensorUnavailable, setSensorUnavailable] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  if (!isOpen) return null;

  const handleSendPacket = async () => {
    setIsSending(true);
    setStatusMsg(null);
    try {
      // Create test-only PPG pulse data; these values are explicitly demo input.
      const rawSamples = Array.from({ length: 250 }, (_, i) => Math.sin((i / 50) * Math.PI * 2) + (Math.random() * 0.08 - 0.04));

      const response = await simulateHardwareTransmission({
        device_id: deviceId,
        patient_id: patientId,
        ppg_samples: sensorUnavailable ? [] : rawSamples,
        signal_quality: sensorUnavailable ? 0.05 : 0.9,
        heart_rate: heartRate,
        spo2: spo2,
      });

      setStatusMsg(`Successfully ingested via /api/v1/ingest/hardware (Risk: ${response.risk_level}, Score: ${response.risk_score})`);
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-lg rounded-3xl border border-slate-800 bg-[#0c121e] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">
                Simulate ESP8266 + MAX30102 Ingestion
              </h2>
              <p className="text-xs text-slate-400">
                POST MAX30102 PPG to <code className="text-cyan-400">/api/v1/ingest/hardware</code>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Controls */}
        <div className="p-6 space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 font-semibold mb-1">Device Node ID</label>
            <input
              type="text"
              value={deviceId}
              onChange={(e) => setDeviceId(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-mono focus:border-cyan-500 outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Test HR (bpm)</label>
              <input
                type="number"
                value={heartRate}
                onChange={(e) => setHeartRate(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-mono focus:border-cyan-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Test SpO2 (%)</label>
              <input
                type="number"
                value={spo2}
                onChange={(e) => setSpo2(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-mono focus:border-cyan-500 outline-none"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="sensorUnavailableCheck"
              checked={sensorUnavailable}
              onChange={(e) => setSensorUnavailable(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-cyan-500"
            />
            <label htmlFor="sensorUnavailableCheck" className="text-slate-300 font-medium cursor-pointer">
              Simulate unavailable optical sensor
            </label>
          </div>

          {statusMsg && (
            <div className={`p-3 rounded-xl border flex items-start gap-2 ${
              statusMsg.startsWith('Error')
                ? 'bg-rose-950/40 border-rose-800 text-rose-300'
                : 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
            }`}>
              {statusMsg.startsWith('Error') ? <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" /> : <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />}
              <span>{statusMsg}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 text-xs font-semibold"
          >
            Done
          </button>
          <button
            onClick={handleSendPacket}
            disabled={isSending}
            className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow transition disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSending ? 'Transmitting...' : 'Send Hardware Packet'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
