import { useEffect, useRef, useState, useCallback } from 'react';
import { VitalData, RiskAnalysisResult, ClinicalAlert, TelemetryPacket } from '../types/vitals';

interface UseVitalsWebSocketOptions {
  patientId?: string;
  maxPpgPoints?: number;
}

export function useVitalsWebSocket({
  patientId = 'PATIENT-001',
  maxPpgPoints = 250
}: UseVitalsWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [currentVital, setCurrentVital] = useState<VitalData | null>(null);
  const [currentRisk, setCurrentRisk] = useState<RiskAnalysisResult | null>(null);
  const [activeAlerts, setActiveAlerts] = useState<ClinicalAlert[]>([]);
  const [ppgBuffer, setPpgBuffer] = useState<number[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);

  const connect = useCallback(() => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const wsBase = import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8000';
    const socketUrl = `${wsBase.replace(/\/$/, '')}/ws/vitals/${patientId}`;
    const ws = new WebSocket(socketUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log(`Connected to Telemetry WebSocket for ${patientId}`);
    };

    ws.onmessage = (event) => {
      if (wsRef.current !== ws) return;
      try {
        const packet: TelemetryPacket = JSON.parse(event.data);
        if (packet.type === 'VITAL_UPDATE') {
          setCurrentVital(packet.vital);
          setCurrentRisk(packet.risk);
          
          if (packet.alerts && packet.alerts.length > 0) {
            setActiveAlerts((prev) => {
              const combined = [...packet.alerts, ...prev];
              // Deduplicate by ID
              const unique = Array.from(new Map(combined.map(a => [a.id, a])).values());
              return unique.slice(0, 10);
            });
          }

          if (packet.vital.ppg_samples && packet.vital.ppg_samples.length > 0) {
            setPpgBuffer((prev) => {
              const updated = [...prev, ...packet.vital.ppg_samples];
              if (updated.length > maxPpgPoints) {
                return updated.slice(updated.length - maxPpgPoints);
              }
              return updated;
            });
          }
        }
      } catch (err) {
        console.error('Failed to parse WebSocket packet:', err);
      }
    };

    ws.onclose = () => {
      if (wsRef.current !== ws) return;
      wsRef.current = null;
      setIsConnected(false);
      console.log('WebSocket disconnected, reconnecting in 2s...');
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 2000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket encountered error:', error);
      ws.close();
    };
  }, [patientId, maxPpgPoints]);

  useEffect(() => {
    setIsConnected(false);
    setCurrentVital(null);
    setCurrentRisk(null);
    setActiveAlerts([]);
    setPpgBuffer([]);
    connect();

    // Heartbeat ping loop
    const pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 10000);

    return () => {
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      const socket = wsRef.current;
      wsRef.current = null;
      if (socket) socket.close();
    };
  }, [connect]);

  const clearAlert = (alertId: number) => {
    setActiveAlerts((prev) => prev.filter(a => a.id !== alertId));
  };

  return {
    isConnected,
    currentVital,
    currentRisk,
    activeAlerts,
    ppgBuffer,
    clearAlert
  };
}
