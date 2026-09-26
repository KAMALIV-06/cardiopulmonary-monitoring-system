import json
import time
from typing import Dict, Set, Any
from fastapi import WebSocket
from app.core.logging import logger

class WebSocketConnectionManager:
    """
    Manages real-time WebSocket connections for continuous patient telemetry streaming.
    Supports patient-specific subscriptions and system broadcasts.
    """

    def __init__(self):
        # Maps patient_id -> Set of active WebSocket connections
        self.patient_connections: Dict[str, Set[WebSocket]] = {}
        # Global connections that observe all patients
        self.global_connections: Set[WebSocket] = set()
        self.hardware_priority_until: Dict[str, float] = {}

    def mark_hardware_active(self, patient_id: str, lease_seconds: float = 15.0):
        self.hardware_priority_until[patient_id] = time.monotonic() + lease_seconds

    def hardware_is_active(self, patient_id: str) -> bool:
        return time.monotonic() < self.hardware_priority_until.get(patient_id, 0.0)

    async def connect(self, websocket: WebSocket, patient_id: str):
        await websocket.accept()
        if patient_id not in self.patient_connections:
            self.patient_connections[patient_id] = set()
        self.patient_connections[patient_id].add(websocket)
        logger.info(f"WebSocket client connected to patient: {patient_id}. Active: {len(self.patient_connections[patient_id])}")

    def disconnect(self, websocket: WebSocket, patient_id: str):
        if patient_id in self.patient_connections:
            self.patient_connections[patient_id].discard(websocket)
            if not self.patient_connections[patient_id]:
                del self.patient_connections[patient_id]
        self.global_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected from patient: {patient_id}")

    async def broadcast_patient_telemetry(self, patient_id: str, data: Dict[str, Any]):
        """
        Broadcasts normalized vitals, PPG samples, risk analysis, and alerts to subscribers.
        """
        if data.get("vital", {}).get("source") == "simulator" and time.monotonic() < self.hardware_priority_until.get(patient_id, 0.0):
            return

        targets = set()
        if patient_id in self.patient_connections:
            targets.update(self.patient_connections[patient_id])
        targets.update(self.global_connections)

        if not targets:
            return

        payload_json = json.dumps(data, default=str)
        dead_sockets = set()

        for connection in targets:
            try:
                await connection.send_text(payload_json)
            except Exception as e:
                dead_sockets.add(connection)

        # Cleanup dead sockets
        for dead in dead_sockets:
            self.disconnect(dead, patient_id)

ws_manager = WebSocketConnectionManager()
