from dataclasses import dataclass

@dataclass
class ScenarioProfile:
    name: str
    description: str
    target_hr: float
    target_spo2: float
    target_rr: float
    hr_variability: float
    ppg_noise_std: float
    arrhythmia_probability: float  # Chance of irregular pulse interval per window
    sensor_unavailable: bool
    signal_quality_base: float

SCENARIOS = {
    "normal": ScenarioProfile(
        name="Normal Sinus Rhythm",
        description="Resting healthy adult. Regular rhythm, optimal blood oxygenation, normal breathing rate.",
        target_hr=72.0,
        target_spo2=98.5,
        target_rr=14.0,
        hr_variability=2.5,
        ppg_noise_std=0.03,
        arrhythmia_probability=0.0,
        sensor_unavailable=False,
        signal_quality_base=0.98
    ),
    "hypoxemia": ScenarioProfile(
        name="Acute Hypoxemic Respiratory Distress",
        description="Sudden desaturation (COPD / COVID-19 / Pneumonia). Rapid shallow tachypneic breathing.",
        target_hr=112.0,
        target_spo2=86.5,
        target_rr=28.0,
        hr_variability=4.0,
        ppg_noise_std=0.05,
        arrhythmia_probability=0.08,
        sensor_unavailable=False,
        signal_quality_base=0.92
    ),
    "tachycardia": ScenarioProfile(
        name="Severe Sinus Tachycardia / Cardiac Stress",
        description="Elevated cardiac rate exceeding 140 bpm — elevated myocardial oxygen demand.",
        target_hr=148.0,
        target_spo2=94.5,
        target_rr=22.0,
        hr_variability=3.0,
        ppg_noise_std=0.04,
        arrhythmia_probability=0.05,
        sensor_unavailable=False,
        signal_quality_base=0.95
    ),
    "bradycardia": ScenarioProfile(
        name="Severe Sinus Bradycardia / Conduction Block",
        description="Pathologically low heart rate (<40 bpm) with compensatory deep breathing.",
        target_hr=36.0,
        target_spo2=93.0,
        target_rr=10.0,
        hr_variability=2.0,
        ppg_noise_std=0.03,
        arrhythmia_probability=0.10,
        sensor_unavailable=False,
        signal_quality_base=0.96
    ),
    "tachypnea": ScenarioProfile(
        name="Isolated Tachypnea / Respiratory Distress",
        description="Rapid shallow breathing without primary hypoxemia — early respiratory fatigue or anxiety.",
        target_hr=88.0,
        target_spo2=95.5,
        target_rr=30.0,
        hr_variability=3.0,
        ppg_noise_std=0.04,
        arrhythmia_probability=0.02,
        sensor_unavailable=False,
        signal_quality_base=0.94
    ),
    "arrhythmia": ScenarioProfile(
        name="Irregular Pulse",
        description="Synthetic irregular pulse intervals for a demo scenario.",
        target_hr=84.0,
        target_spo2=95.0,
        target_rr=16.0,
        hr_variability=15.0,
        ppg_noise_std=0.06,
        arrhythmia_probability=0.35,
        sensor_unavailable=False,
        signal_quality_base=0.88
    ),
    "sensor_disconnect": ScenarioProfile(
        name="Optical Sensor Disconnect",
        description="Optical sensor unavailable ; simulated PPG signal quality is low.",
        target_hr=0.0,
        target_spo2=0.0,
        target_rr=0.0,
        hr_variability=0.0,
        ppg_noise_std=0.4,
        arrhythmia_probability=0.0,
        sensor_unavailable=True,
        signal_quality_base=0.08
    ),
}

# All valid scenario keys (exported for use by simulator endpoint)
VALID_SCENARIO_KEYS = list(SCENARIOS.keys())
