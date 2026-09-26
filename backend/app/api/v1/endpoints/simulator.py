import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

class ScenarioChangeRequest(BaseModel):
    scenario: str = Field(..., json_schema_extra={"example": "hypoxemia"})
    patient_id: str = Field(default="PATIENT-001")

# Reference to simulator controller (wired in main.py via register_sim_controller)
_sim_controller = None

VALID_SCENARIOS = [
    "normal",
    "hypoxemia",
    "tachycardia",
    "bradycardia",
    "tachypnea",
    "arrhythmia",
    "sensor_disconnect"
]

def register_sim_controller(controller):
    global _sim_controller
    _sim_controller = controller

@router.get("/simulator/status", summary="Get Simulator Status")
async def get_simulator_status():
    """Returns the current state of the physiological simulator."""
    if not _sim_controller:
        return {"running": False, "scenario": "unknown", "message": "Simulator controller not initialized"}
    return {
        "running": _sim_controller.is_running,
        "scenario": _sim_controller.current_scenario,
        "patient_id": _sim_controller.patient_id,
        "tick_rate_hz": _sim_controller.tick_rate_hz,
        "available_scenarios": VALID_SCENARIOS
    }

@router.post("/simulator/start", summary="Start Simulator")
async def start_simulator():
    """Start the background physiological simulator."""
    if not _sim_controller:
        raise HTTPException(status_code=500, detail="Simulator controller not registered")
    await _sim_controller.start()
    return {"status": "started", "scenario": _sim_controller.current_scenario}

@router.post("/simulator/stop", summary="Stop Simulator")
async def stop_simulator():
    """Stop the background physiological simulator."""
    if not _sim_controller:
        raise HTTPException(status_code=500, detail="Simulator controller not registered")
    await _sim_controller.stop()
    return {"status": "stopped"}

@router.post("/simulator/scenario", summary="Change Simulator Scenario")
async def set_simulator_scenario(request: ScenarioChangeRequest):
    """
    Change the active physiological simulation scenario.
    Transitions are gradual — values interpolate toward new targets.
    Available scenarios: normal, hypoxemia, tachycardia, bradycardia,
                         tachypnea, arrhythmia, sensor_disconnect
    """
    if not _sim_controller:
        raise HTTPException(status_code=500, detail="Simulator controller not registered")

    if request.scenario not in VALID_SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario '{request.scenario}'. Must be one of: {VALID_SCENARIOS}"
        )

    _sim_controller.set_scenario(request.scenario)
    if request.patient_id:
        _sim_controller.patient_id = request.patient_id

    return {
        "status": "updated",
        "scenario": _sim_controller.current_scenario,
        "patient_id": _sim_controller.patient_id,
        "message": f"Physiological simulation transitioning to: {request.scenario}"
    }
