import React, { useEffect, useState } from 'react';
import { AlertTriangle, ChevronDown, FileText, Users } from 'lucide-react';
import { Navbar } from './components/Navbar';
import { PpgWaveformCanvas } from './components/PpgWaveformCanvas';
import { VitalCard } from './components/VitalCard';
import { RiskScoreGauge } from './components/RiskScoreGauge';
import { AlertBanner } from './components/AlertBanner';
import { HardwareStatusBadge } from './components/HardwareStatusBadge';
import { SimulatorControlModal } from './components/SimulatorControlModal';
import { HardwareTestModal } from './components/HardwareTestModal';
import { HistoricalTrends } from './components/HistoricalTrends';
import { AlertsPanel } from './components/AlertsPanel';
import { DevicePanel } from './components/DevicePanel';
import { Sidebar } from './components/Sidebar';
import { PatientDirectory } from './components/PatientDirectory';
import { ClinicalProfile } from './components/ClinicalProfile';
import { PatientPanel } from './components/PatientPanel';
import { useVitalsWebSocket } from './hooks/useVitalsWebSocket';
import { fetchPatients } from './services/api';
import type { Patient } from './types/patient';

export type SidebarPage = 'overview' | 'monitoring' | 'trends' | 'alerts' | 'devices' | 'patients' | 'clinical' | 'settings';

export const App: React.FC = () => {
  const [patientId, setPatientId] = useState('PATIENT-001');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);
  const [isHardwareTestOpen, setIsHardwareTestOpen] = useState(false);
  const [currentScenario, setCurrentScenario] = useState('normal');
  const [activePage, setActivePage] = useState<SidebarPage>('overview');
  const { isConnected, currentVital, currentRisk, activeAlerts, ppgBuffer, clearAlert } = useVitalsWebSocket({ patientId });

  useEffect(() => {
    let alive = true;
    fetchPatients().then(rows => {
      if (!alive) return;
      setPatients(rows);
      if (rows.length && !rows.some(row => row.id === patientId)) setPatientId(rows[0].id);
    }).catch(() => undefined);
    return () => { alive = false; };
  }, []);


  const hr = currentVital?.heart_rate ?? 0;
  const spo2 = currentVital?.spo2 ?? 0;
  const rr = currentVital?.respiratory_rate ?? 0;
  const source = currentVital?.source;

  const sourceLabel = source === 'hardware' ? 'LIVE HARDWARE · ESP8266 + MAX30102'
    : source === 'simulator' ? 'SIMULATOR · Scenario data'
      : source === 'dataset' ? 'DATASET REPLAY · Historical synthetic readings' : 'WAITING FOR DATA';
  const getHrStatus = () => hr === 0 ? 'Unavailable' : hr > 130 ? 'Very high measurement' : hr > 100 ? 'Elevated measurement' : hr <= 40 ? 'Very low measurement' : hr < 50 ? 'Low measurement' : 'Within configured range';
  const getSpo2Status = () => spo2 === 0 ? 'Unavailable' : spo2 <= 91 ? 'Low measurement' : spo2 <= 94 ? 'Borderline measurement' : 'Within configured range';
  const getRrStatus = () => rr === 0 ? 'Unavailable' : rr >= 25 ? 'High measurement' : rr > 20 ? 'Elevated measurement' : rr <= 8 ? 'Low measurement' : 'Within configured range';

  const cards = <section className="grid grid-cols-1 gap-5 md:grid-cols-3">
    <VitalCard type="hr" label="Heart rate" value={hr} unit="BPM" normalRange="60–100" isWarning={hr > 100 || (hr > 0 && hr < 50)} isCritical={hr > 130 || (hr > 0 && hr <= 40)} statusText={getHrStatus()} source={source}/>
    <VitalCard type="spo2" label="SpO₂ · device estimate" value={spo2} unit="%" normalRange="95–100" isWarning={spo2 > 0 && spo2 < 95} isCritical={spo2 > 0 && spo2 <= 91} statusText={getSpo2Status()} source={source}/>
    <VitalCard type="rr" label={`Respiratory rate · ${source === 'hardware' ? 'PPG-derived estimate' : source === 'simulator' ? 'simulated' : source === 'dataset' ? 'recorded dataset' : 'source pending'}`} value={rr} unit="/min" normalRange="12–20" isWarning={rr > 20 || (rr > 0 && rr < 11)} isCritical={rr > 24 || (rr > 0 && rr <= 8)} statusText={getRrStatus()} source={source}/>
  </section>;

  const renderContent = () => {
    switch (activePage) {
      case 'monitoring':
        return <div className="space-y-6">
          <header><h2 className="text-xl font-bold text-white">Live Monitoring</h2><p className="mt-1 text-sm text-slate-400">Real-time signal, device health, and source-labelled telemetry for {patientId}.</p></header>
          <HardwareStatusBadge vital={currentVital}/>
          <PpgWaveformCanvas ppgBuffer={ppgBuffer} height={260}/>
          {cards}
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/50 p-4 text-xs text-slate-300"><span>Source: {sourceLabel}</span><span>Last update: {currentVital ? new Date(currentVital.timestamp).toLocaleString() : 'Waiting for telemetry'}</span><span>WebSocket: {isConnected ? 'Connected' : 'Reconnecting'}</span></div>
          <p className="text-xs text-slate-500">MAX30102 provides optical PPG with device-calculated heart rate and SpO₂ estimates. Respiratory rate is derived from sufficiently long PPG windows; it is not a direct sensor measurement. Transparent baseline risk indication — not a diagnosis.</p>
        </div>;
      case 'patients':
        return <PatientDirectory selectedPatientId={patientId} onSelect={id => { setPatientId(id); setActivePage('clinical'); }}/>
      case 'clinical':
        return <ClinicalProfile patientId={patientId}/>;
      case 'alerts':
        return <AlertsPanel patientId={patientId} liveAlerts={activeAlerts}/>;
      case 'devices':
        return <DevicePanel vital={currentVital} isConnected={isConnected} onOpenHardwareTest={() => setIsHardwareTestOpen(true)} onOpenSimulator={() => setIsSimulatorOpen(true)}/>;
      case 'trends':
        return <div className="space-y-5"><header><h2 className="text-xl font-bold text-white">Trends</h2><p className="mt-1 text-sm text-slate-400">Historical telemetry with source labels and selectable measures.</p></header><HistoricalTrends patientId={patientId} expanded/></div>;
      case 'settings':
        return <div className="space-y-5"><header><h2 className="text-xl font-bold text-white">Settings</h2><p className="mt-1 text-sm text-slate-400">Demo controls and current application configuration.</p></header>
          <section className="grid gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-5 sm:grid-cols-2"><button onClick={() => setIsSimulatorOpen(true)} className="rounded-xl border border-emerald-500/30 bg-emerald-600/10 p-4 text-left text-sm font-semibold text-emerald-200">Open scenario simulator</button><button onClick={() => setIsHardwareTestOpen(true)} className="rounded-xl border border-cyan-500/30 bg-cyan-600/10 p-4 text-left text-sm font-semibold text-cyan-200">Send hardware test packet</button><div className="text-xs text-slate-400">API: {import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'}</div><div className="text-xs text-slate-400">Selected patient: {patientId}</div></section>
          <p className="text-xs text-slate-500">Demo controls generate synthetic telemetry. They do not represent a patient measurement.</p></div>;
      default:
        return <div className="space-y-6">
          <AlertBanner alerts={activeAlerts} onDismiss={clearAlert}/>
          <section className="rounded-2xl border border-slate-800 bg-[#0e1626] p-4 sm:flex sm:items-center sm:justify-between"><div><p className="text-xs font-semibold uppercase tracking-widest text-slate-500">Selected patient · monitoring {currentVital ? 'active' : 'waiting'}</p><p className="mt-1 text-sm font-semibold text-cyan-200">{sourceLabel}</p></div><p className="mt-2 text-xs text-slate-400 sm:mt-0">Patient values and sensor values are shown separately.</p></section>
          {cards}
          <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]"><RiskScoreGauge risk={currentRisk}/><PatientPanel patientId={patientId} vital={currentVital} risk={currentRisk} isConnected={isConnected} monitoringStart={currentVital?.timestamp ?? null}/></div>
          <HistoricalTrends patientId={patientId}/>
          <p className="flex items-start gap-2 text-xs text-slate-500"><AlertTriangle className="h-4 w-4 shrink-0 text-amber-400"/>Transparent baseline risk indication — not a diagnosis. Clinical context is synthetic where marked and must be reviewed by a healthcare professional.</p>
        </div>;
    }
  };

  return <div className="flex min-h-screen flex-col bg-[#070b12] font-sans text-slate-100">
    <Navbar isConnected={isConnected} source={source} patientId={patientId} onOpenSimulator={() => setIsSimulatorOpen(true)} onOpenHardwareTest={() => setIsHardwareTestOpen(true)}/>
    <div className="flex flex-1 overflow-hidden">
      <Sidebar activePage={activePage} onNavigate={setActivePage} alertCount={activeAlerts.filter(a => !a.acknowledged).length} riskLevel={currentRisk?.risk_level} isConnected={isConnected}/>
      <main className="flex-1 overflow-y-auto p-4 lg:p-6 xl:p-8"><div className="mx-auto max-w-7xl space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/40 px-4 py-3">
          <label htmlFor="patient-selector" className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400"><Users className="h-4 w-4 text-cyan-300"/>Monitoring patient</label>
          <div className="relative"><select id="patient-selector" value={patientId} onChange={event => setPatientId(event.target.value)} className="min-w-64 appearance-none rounded-lg border border-slate-700 bg-slate-950 py-2 pl-3 pr-9 text-sm text-white focus:border-cyan-500 focus:outline-none">
            {!patients.some(patient => patient.id === patientId) && <option value={patientId}>{patientId}</option>}
            {patients.map(patient => <option key={patient.id} value={patient.id}>{patient.name} · {patient.id}{patient.demo_data ? ' · DEMO' : ''}</option>)}
          </select><ChevronDown className="pointer-events-none absolute right-3 top-2.5 h-4 w-4 text-slate-500"/></div>
          {activePage !== 'clinical' && <button onClick={() => setActivePage('clinical')} className="flex items-center gap-1.5 text-xs text-cyan-300 hover:text-cyan-200"><FileText className="h-4 w-4"/>Clinical profile</button>}
        </div>
        {renderContent()}
        <footer className="border-t border-slate-800 pt-4 text-center text-[11px] text-slate-500">Care-team monitoring support · Transparent baseline risk indication — not a diagnosis. Synthetic records are clearly marked.</footer>
      </div></main>
    </div>
    <SimulatorControlModal isOpen={isSimulatorOpen} onClose={() => setIsSimulatorOpen(false)} currentScenario={currentScenario} patientId={patientId} onScenarioChange={setCurrentScenario}/>
    <HardwareTestModal isOpen={isHardwareTestOpen} onClose={() => setIsHardwareTestOpen(false)} patientId={patientId}/>
  </div>;
};

export default App;
