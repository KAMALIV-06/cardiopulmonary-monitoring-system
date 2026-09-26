from abc import ABC, abstractmethod
from typing import Any
from app.schemas.vital import VitalData

class BaseDataSourceAdapter(ABC):
    """
    Abstract Ingestion Adapter.
    Guarantees hardware independence across simulator, recorded datasets, and connected hardware.
    """
    
    @abstractmethod
    def normalize(self, raw_payload: Any) -> VitalData:
        """
        Normalize arbitrary raw sensor input into the standardized VitalData schema.
        """
        pass
