import asyncio
import datetime
from typing import Optional
from app.core.logging import logger
from app.database.session import AsyncSessionLocal
from app.data_sources.simulator_adapter import SimulatorAdapter
from app.api.v1.endpoints.vitals import process_and_persist_vital
from app.websocket.manager import ws_manager
from simulator.physiological_simulator import PhysiologicalSimulator

class SimulatorController:
    """
    Manages the background physiological simulation worker.
    Continuously ingests simulated frames into the backend pipeline.
    """
    def __init__(self):
        self.simulator = PhysiologicalSimulator(sampling_rate_hz=50)
        self.is_running = False
        self.patient_id = "PATIENT-001"
        self.current_scenario = "normal"
        self.tick_rate_hz = 2  # Two 25-sample PPG windows per second.
        self._task: Optional[asyncio.Task] = None
        self._adapter = SimulatorAdapter()

    def set_scenario(self, scenario: str):
        self.current_scenario = scenario
        self.simulator.set_scenario(scenario)
        logger.info(f"Simulator scenario switched to: {scenario}")

    async def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Physiological Simulator background runner STARTED.")

    async def stop(self):
        if self.is_running:
            self.is_running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("Physiological Simulator background runner STOPPED.")

    async def _run_loop(self):
        interval = 1.0 / self.tick_rate_hz
        while self.is_running:
            try:
                if ws_manager.hardware_is_active(self.patient_id):
                    await asyncio.sleep(interval)
                    continue
                # 1. Generate realistic window (25 samples)
                raw_window = self.simulator.generate_window(
                    num_samples=25,
                    patient_id=self.patient_id,
                    device_id="SIM-PHYSIO-01"
                )
                
                # 2. Normalize using SimulatorAdapter
                normalized_vital = self._adapter.normalize(raw_window)

                # 3. Ingest into database and broadcast over WebSocket
                async with AsyncSessionLocal() as session:
                    await process_and_persist_vital(normalized_vital, session)

                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in simulator background loop: {e}")
                await asyncio.sleep(1.0)

simulator_controller = SimulatorController()
