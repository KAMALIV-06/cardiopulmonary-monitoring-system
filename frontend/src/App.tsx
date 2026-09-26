import React, { useEffect, useState } from 'react';
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
import { PatientPanel } from './components/PatientPanel';
import { DevicePanel } from './components/DevicePanel';
import { Sidebar } from './components/Sidebar';
import { useVitalsWebSocket } from './hooks/useVitalsWebSocket';

export type SidebarPage = 'overview' | 'monitoring' | 'trends' | 'alerts' | 'devices' | 'patients' | 'settings';

export const App: React.FC = () => {
  const patientId = 'PATIENT-001';
  const {
    isConnected,
    currentVital,
    currentRisk,
    activeAlerts,
    ppgBuffer,
    clearAlert
  } = useVitalsWebSocket({ patientId });

  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);
  const [isHardwareTestOpen, setIsHardwareTestOpen] = useState(false);
  const [currentScenario, setCurrentScenario] = useState('normal');
  const [activePage, setActivePage] = useState<SidebarPage>('overview');
  const [monitoringStart, setMonitoringStart] = useState<string | null>(null);
  useEffect(() => {
    if (currentVital && !monitoringStart) setMonitoringStart(currentVital.timestamp);
  }, [currentVital, monitoringStart]);

  // Computed vitals from backend data
  const hr = currentVital?.heart_rate ?? 0;
  const spo2 = currentVital?.spo2 ?? 0;
  const rr = currentVital?.respiratory_rate ?? 0;
  const sqi = currentVital?.signal_quality ?? 0;
  const source = currentVital?.source;

  const isHrWarning = hr > 100 || (hr > 0 && hr < 50);
  const isHrCritical = hr > 130 || (hr > 0 && hr <= 40);
  const isSpo2Warning = spo2 > 0 && spo2 < 95;
  const isSpo2Critical = spo2 > 0 && spo2 <= 91;
  const isRrWarning = rr > 20 || (rr > 0 && rr < 11);
  const isRrCritical = rr > 24 || (rr > 0 && rr <= 8);

  const getHrStatus = () => {
    if (hr === 0) return 'No Signal';
    if (hr > 130) return 'Severe Tachycardia';
    if (hr > 100) return 'Tachycardia';
    if (hr <= 40) return 'Severe Bradycardia';
    if (hr < 50) return 'Bradycardia';
    return 'Normal Sinus';
  };

  const getSpo2Status = () => {
    if (spo2 === 0) return 'No Signal';
    if (spo2 <= 91) return 'Severe Hypoxia';
    if (spo2 <= 94) return 'Borderline';
    return 'Optimal';
  };

  const getRrStatus = () => {
    if (rr === 0) return source === 'hardware' ? 'Estimate unavailable' : 'No Signal';
    if (rr >= 25) return 'Tachypnea (Distress)';
    if (rr > 20) return 'Elevated';
    if (rr <= 8) return 'Bradypnea';
    return 'Eupneic (Normal)';
  };

  const renderPageContent = () => {
    switch (activePage) {
      case 'alerts':
        return (
          <AlertsPanel patientId={patientId} liveAlerts={activeAlerts} />
        );
      case 'devices':
        return (
          <DevicePanel
            vital={currentVital}
            isConnected={isConnected}
            onOpenHardwareTest={() => setIsHardwareTestOpen(true)}
            onOpenSimulator={() => setIsSimulatorOpen(true)}
          />
        );
      case 'patients':
        return (
          <PatientPanel
            patientId={patientId}
            vital={currentVital}
            risk={currentRisk}
            isConnected={isConnected}
            monitoringStart={monitoringStart}
          />
        );
      case 'trends':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">Physiological Trends</h2>
              <p className="text-sm text-slate-400">Historical vital sign data from backend database</p>
            </div>
            <HistoricalTrends patientId={patientId} expanded />
          </div>
        );
      case 'settings':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">System Settings</h2>
              <p className="text-sm text-slate-400">Configuration and demo controls</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Demo Controls</h3>
                <button
                  onClick={() => setIsSimulatorOpen(true)}
                  className="w-full py-3 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-sm font-semibold transition"
                >
                  Open Scenario Simulator
                </button>
                <button
                  onClick={() => setIsHardwareTestOpen(true)}
                  className="w-full py-3 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-sm font-semibold transition"
                >
                  Simulate MAX30102 Hardware Ingestion
                </button>
              </div>
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-3">
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider">System Info</h3>
                <div className="space-y-2 text-xs text-slate-400">
                  <div className="flex justify-between"><span>Backend</span><span className="text-slate-300 font-mono">localhost:8000</span></div>
                  <div className="flex justify-between"><span>WebSocket</span><span className="text-slate-300 font-mono">ws://localhost:8000</span></div>
                  <div className="flex justify-between"><span>Patient ID</span><span className="text-slate-300 font-mono">{patientId}</span></div>
                  <div className="flex justify-between"><span>API Docs</span><span className="text-slate-300 font-mono">localhost:8000/docs</span></div>
                </div>
              </div>
            </div>
          </div>
        );
      default: // 'overview' and 'monitoring'
        return (
          <div className="space-y-6">
            {/* Alert Banner */}
            <AlertBanner alerts={activeAlerts} onDismiss={clearAlert} />

            {/* Hardware Status */}
            <HardwareStatusBadge vital={currentVital} />

            {/* Live PPG Waveform */}
            <section>
              <PpgWaveformCanvas
                ppgBuffer={ppgBuffer}
                signalQuality={sqi}
                height={220}
              />
            </section>

            {/* Vital Cards */}
            <section className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <VitalCard
                type="hr"
                label="Heart Rate (MAX30102)"
                value={hr}
                unit="BPM"
                normalRange="60 – 100"
                isWarning={isHrWarning}
                isCritical={isHrCritical}
                statusText={getHrStatus()}
              />
              <VitalCard
                type="spo2"
                label="Blood Oxygen (SpO2)"
                value={spo2}
                unit="%"
                normalRange="95 – 100"
                isWarning={isSpo2Warning}
                isCritical={isSpo2Critical}
                statusText={getSpo2Status()}
              />
              <VitalCard
                type="rr"
                label={`Respiratory Rate (${source === 'hardware' ? 'PPG estimate' : source === 'simulator' ? 'simulated' : source === 'dataset' ? 'recorded' : 'estimate'})`}
                value={rr}
                unit="/min"
                normalRange="12 – 20"
                isWarning={isRrWarning}
                isCritical={isRrCritical}
                statusText={getRrStatus()}
              />
            </section>

            {/* Risk + Trends */}
            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RiskScoreGauge risk={currentRisk} />
              <HistoricalTrends patientId={patientId} />
            </section>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <Navbar
        isConnected={isConnected}
        source={source}
        patientId={patientId}
        onOpenSimulator={() => setIsSimulatorOpen(true)}
        onOpenHardwareTest={() => setIsHardwareTestOpen(true)}
      />

      {/* Main Layout: Sidebar + Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Navigation */}
        <Sidebar
          activePage={activePage}
          onNavigate={setActivePage}
          alertCount={activeAlerts.filter(a => !a.acknowledged).length}
          riskLevel={currentRisk?.risk_level}
          isConnected={isConnected}
        />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 xl:p-8">
          <div className="max-w-6xl mx-auto">
            {renderPageContent()}
          </div>
        </main>
      </div>

      {/* Demo Mode Modal */}
      <SimulatorControlModal
        isOpen={isSimulatorOpen}
        onClose={() => setIsSimulatorOpen(false)}
        currentScenario={currentScenario}
        onScenarioChange={(sc) => setCurrentScenario(sc)}
      />

      {/* Hardware Test Modal */}
      <HardwareTestModal
        isOpen={isHardwareTestOpen}
        onClose={() => setIsHardwareTestOpen(false)}
        patientId={patientId}
      />
    </div>
  );
};

export default App;
