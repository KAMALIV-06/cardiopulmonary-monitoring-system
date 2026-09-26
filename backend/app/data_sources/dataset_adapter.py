import datetime
from typing import Dict, Any
from app.data_sources.base import BaseDataSourceAdapter
from app.schemas.vital import VitalData
from app.services.signal_processing import signal_service

class DatasetAdapter(BaseDataSourceAdapter):
    """
    Adapter for replaying recorded clinical datasets (e.g. MIT-BIH Arrhythmia, PhysioNet).
    """

    def normalize(self, raw_payload: Dict[str, Any]) -> VitalData:
        return VitalData(
            patient_id=str(raw_payload.get("patient_id", "DATASET-SUBJECT-01")),
            device_id=str(raw_payload.get("device_id", "PHYSIONET-REPLAY")),
            timestamp=raw_payload.get("timestamp") or datetime.datetime.now(datetime.timezone.utc),
            heart_rate=float(raw_payload["heart_rate"]),
            spo2=float(raw_payload["spo2"]),
            respiratory_rate=float(raw_payload["respiratory_rate"]),
            ppg_samples=[float(x) for x in raw_payload.get("ppg_samples", [])],
            signal_quality=float(raw_payload.get("signal_quality", signal_service.calculate_sqi(raw_payload.get("ppg_samples", [])))),
            source="dataset"
        )
