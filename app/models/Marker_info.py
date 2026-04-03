from pydantic import BaseModel
from typing import Any

class Marker_info(BaseModel):
    dictionary_name: str
    marker_id: int
    payload_type: str
    payload: Any  # JSONB можно хранить как dict