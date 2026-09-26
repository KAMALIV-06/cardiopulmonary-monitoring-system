from typing import List, Dict
import numpy as np


class SignalProcessingService:
    """Small PPG utilities; respiratory rate is withheld without enough data."""

    @staticmethod
    def filter_ppg(samples: List[float]) -> List[float]:
        if len(samples) < 3:
            return samples
        values = np.asarray(samples, dtype=float)
        centered = values - np.mean(values)
        return [round(float(v), 5) for v in np.convolve(centered, np.ones(3) / 3, mode="same")]

    @staticmethod
    def calculate_sqi(samples: List[float]) -> float:
        if len(samples) < 10:
            return 0.1
        values = np.asarray(samples, dtype=float)
        if not np.all(np.isfinite(values)) or float(np.std(values)) < 1e-8:
            return 0.05
        q25, q75 = np.percentile(values, [25, 75])
        spread = float(q75 - q25)
        if spread <= 1e-8:
            return 0.1
        # A bounded signal variation heuristic, not a clinical PPG quality classifier.
        return round(float(np.clip(spread / (np.std(values) * 2.0), 0.2, 1.0)), 2)

    @staticmethod
    def estimate_respiratory_rate(samples: List[float], sample_rate_hz: float = 50.0) -> float:
        """Estimate respiratory modulation only from >=20 s of PPG; else return unavailable (0)."""
        if len(samples) < int(sample_rate_hz * 20):
            return 0.0
        values = np.asarray(samples, dtype=float)
        if not np.all(np.isfinite(values)) or np.std(values) < 1e-8:
            return 0.0
        # Smooth the pulse amplitude envelope, then find its strongest plausible
        # respiratory modulation frequency (6-40 breaths/minute).
        window = max(3, int(sample_rate_hz * 0.5))
        envelope = np.convolve(np.abs(values - np.mean(values)), np.ones(window) / window, mode="same")
        envelope -= np.mean(envelope)
        spectrum = np.abs(np.fft.rfft(envelope))
        frequencies = np.fft.rfftfreq(len(envelope), d=1.0 / sample_rate_hz)
        band = (frequencies >= 0.1) & (frequencies <= 0.67)
        if not np.any(band) or np.max(spectrum[band]) <= 1e-8:
            return 0.0
        rate = frequencies[band][int(np.argmax(spectrum[band]))] * 60.0
        return round(float(rate), 1)

    @staticmethod
    def analyze_hrv(rr_intervals_ms: List[float]) -> Dict[str, float]:
        if len(rr_intervals_ms) < 2:
            return {}
        rr = np.asarray(rr_intervals_ms, dtype=float)
        return {
            "mean_rr": round(float(np.mean(rr)), 1),
            "sdnn": round(float(np.std(rr, ddof=1)), 1),
            "rmssd": round(float(np.sqrt(np.mean(np.diff(rr) ** 2))), 1),
        }


signal_service = SignalProcessingService()
