import React, { useEffect, useState } from 'react';
import { VitalData } from '../types/vitals';

interface DevicePanelProps {
  vital: VitalData | null;
  isConnected: boolean;
  onOpenHardwareTest: () => void;
  onOpenSimulator: () => void;
}

export const DevicePanel: React.FC<DevicePanelProps> = ({ vital, isConnected, onOpenHardwareTest, onOpenSimulator }) => {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  const lastSeen = vital ? new Date(vital.timestamp) : null;
  const fresh = lastSeen !== null && now - lastSeen.getTime() < 15000;
  const deviceType = vital?.source === 'hardware' ? 'ESP8266 + MAX30102' : vital?.source === 'simulator' ? 'Scenario Simulator' : vital?.source === 'dataset' ? 'Historical Dataset Replay' : 'Unknown';
  const sourceLabel = vital?.source === 'hardware' ? 'HARDWARE' : vital?.source === 'simulator' ? 'SIMULATOR' : vital?.source === 'dataset' ? 'DATASET REPLAY' : 'Waiting';

  return (
    <section className="rounded-2xl border border-slate-800 bg-[#0e1626] p-6">
      <h2 className="text-lg font-bold text-white">Active device</h2>
      <p className="mb-5 text-sm text-slate-400">Device and ingestion status for the selected patient. Live hardware uses the existing ESP8266 + MAX30102 adapter.</p>
      <dl className="grid gap-4 sm:grid-cols-2 text-sm">
        <div><dt className="text-slate-500">Device ID</dt><dd className="mt-1 text-white">{vital?.device_id ?? 'Waiting for telemetry'}</dd></div>
        <div><dt className="text-slate-500">Device type</dt><dd className="mt-1 text-white">{deviceType}</dd></div>
        <div><dt className="text-slate-500">Source</dt><dd className="mt-1 text-white">{sourceLabel}</dd></div>
        <div><dt className="text-slate-500">Device reporting</dt><dd className="mt-1 text-white">{fresh ? vital?.source === 'hardware' ? 'Recent hardware packet' : `Recent ${sourceLabel.toLowerCase()} data` : isConnected ? 'WebSocket online · awaiting fresh data' : 'No recent data'}</dd></div>
        <div><dt className="text-slate-500">Last seen</dt><dd className="mt-1 text-white">{lastSeen ? lastSeen.toLocaleString() : 'No reading yet'}</dd></div>
        <div><dt className="text-slate-500">Signal quality</dt><dd className="mt-1 text-white">{vital ? `${(vital.signal_quality * 100).toFixed(0)}%` : 'No data'}</dd></div>
      </dl>
      <div className="mt-6 flex flex-wrap gap-3">
        <button onClick={onOpenSimulator} className="rounded-lg bg-emerald-700 px-4 py-2 text-sm text-white">Demo scenarios</button>
        <button onClick={onOpenHardwareTest} className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-white">Send MAX30102 test sample</button>
      </div>
    </section>
  );
};
