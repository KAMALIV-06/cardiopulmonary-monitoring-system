import math
import random
import datetime
from typing import List, Dict, Any

try:
    from simulator.scenarios import SCENARIOS, ScenarioProfile
except ImportError:
    from scenarios import SCENARIOS, ScenarioProfile


class PhysiologicalSimulator:
    """Synthetic PPG and vital generator for development/demo use only."""

    def __init__(self, sampling_rate_hz: int = 50):
        self.sampling_rate_hz = sampling_rate_hz
        self.current_scenario_key = "normal"
        self.profile: ScenarioProfile = SCENARIOS["normal"]
        self.current_hr = self.profile.target_hr
        self.current_spo2 = self.profile.target_spo2
        self.current_rr = self.profile.target_rr
        self.phase = 0.0
        self.resp_phase = 0.0
        self.time_step = 1.0 / self.sampling_rate_hz

    def set_scenario(self, scenario_key: str):
        if scenario_key in SCENARIOS:
            self.current_scenario_key = scenario_key
            self.profile = SCENARIOS[scenario_key]

    def _pulse(self, phase: float) -> float:
        # Stylized optical pulse: fast systolic rise and broader decay. Not a sensor model.
        rise = math.exp(-((phase - 0.16) ** 2) / 0.003)
        decay = 0.35 * math.exp(-((phase - 0.34) ** 2) / 0.02)
        return rise + decay

    def generate_window(self, num_samples: int = 25, patient_id: str = "PATIENT-001", device_id: str = "SIM-PHYSIO-01") -> Dict[str, Any]:
        alpha = 0.05
        self.current_hr += alpha * (self.profile.target_hr - self.current_hr)
        self.current_spo2 += alpha * (self.profile.target_spo2 - self.current_spo2)
        self.current_rr += alpha * (self.profile.target_rr - self.current_rr)
        hr = self.current_hr + random.gauss(0, self.profile.hr_variability * 0.1)
        spo2 = min(100.0, max(60.0, self.current_spo2 + random.gauss(0, 0.2)))
        rr = max(4.0, self.current_rr + random.gauss(0, 0.3))
        unavailable = self.profile.sensor_unavailable
        if unavailable:
            hr = spo2 = rr = 0.0

        samples: List[float] = []
        for _ in range(num_samples):
            if unavailable:
                value = random.gauss(0, self.profile.ppg_noise_std)
            else:
                freq = max(0.1, hr / 60.0)
                resp_freq = max(0.05, rr / 60.0)
                self.resp_phase = (self.resp_phase + resp_freq * self.time_step) % 1.0
                previous_phase = self.phase
                self.phase = (self.phase + freq * self.time_step) % 1.0
                if self.phase < previous_phase and random.random() < self.profile.arrhythmia_probability:
                    # Demo-only irregular pulse interval; it is not an ECG rhythm diagnosis.
                    self.phase = (self.phase + random.choice((-0.12, 0.12))) % 1.0
                amplitude = 1.0 + 0.08 * math.sin(2 * math.pi * self.resp_phase)
                value = amplitude * self._pulse(self.phase) + random.gauss(0, self.profile.ppg_noise_std)
            samples.append(round(value, 5))

        sqi = 0.05 if unavailable else max(0.05, min(1.0, self.profile.signal_quality_base + random.gauss(0, 0.02)))
        return {
            "patient_id": patient_id,
            "device_id": device_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "heart_rate": round(hr, 1),
            "spo2": round(spo2, 1),
            "respiratory_rate": round(rr, 1),
            "ppg_samples": samples,
            "signal_quality": round(sqi, 2),
            "source": "simulator",
        }


if __name__ == "__main__":
    sim = PhysiologicalSimulator()
    for key in SCENARIOS:
        sim.set_scenario(key)
        data = sim.generate_window(25)
        print(f"[{key.upper()}] HR: {data['heart_rate']} bpm | SpO2: {data['spo2']}% | RR: {data['respiratory_rate']} | SQI: {data['signal_quality']} | PPG samples: {len(data['ppg_samples'])}")
