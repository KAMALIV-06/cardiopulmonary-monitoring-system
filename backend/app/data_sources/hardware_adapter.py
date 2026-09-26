import datetime
from typing import Union, Dict, Any
from app.data_sources.base import BaseDataSourceAdapter
from app.schemas.vital import VitalData
from app.schemas.hardware import HardwarePayload
from app.services.signal_processing import signal_service

class HardwareAdapter(BaseDataSourceAdapter):
    """
    Adapter for a networked microcontroller with:
    - MAX30102 (PPG / Heart Rate / SpO2)
    - PPG waveform and device-derived heart rate / SpO2
    """

    def normalize(self, raw_payload: Union[HardwarePayload, Dict[str, Any]]) -> VitalData:
        if isinstance(raw_payload, dict):
            payload = HardwarePayload(**raw_payload)
        else:
            payload = raw_payload

        samples = payload.ppg_samples or [float(x) for x in (payload.ppg_ir_samples or [])]
        quality = payload.signal_quality
        if quality is None:
            quality = signal_service.calculate_sqi(samples)
        # MAX30102 has no direct respiration channel. Short windows return 0
        # (unavailable) until enough PPG history exists for an estimate.
        rr = signal_service.estimate_respiratory_rate(samples)

        return VitalData(
            patient_id=payload.patient_id,
            device_id=payload.device_id,
            timestamp=payload.timestamp or datetime.datetime.now(datetime.timezone.utc),
            heart_rate=payload.heart_rate,
            spo2=payload.spo2,
            respiratory_rate=rr,
            ppg_samples=samples,
            signal_quality=quality,
            source="hardware"
        )
