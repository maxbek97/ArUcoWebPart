from pydantic import BaseModel
from typing import Any
from fastapi import Form
from typing import Annotated

class MarkerInfoDTO(BaseModel):
    dictionary_name: str
    marker_id: int
    payload_type: str
    payload: Any  # JSONB можно хранить как dict

class MarkerForm:
    def __init__(
        self,
        dictionary_name: Annotated[str, Form(...)],
        marker_id: Annotated[int, Form(...)],
        payload_type: Annotated[str, Form(...)],
        payload: Annotated[str, Form(...)],  # JSON строка
    ):
        self.dictionary_name = dictionary_name
        self.marker_id = marker_id
        self.payload_type = payload_type
        self.payload = payload