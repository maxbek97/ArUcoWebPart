from pydantic import BaseModel

class DictionaryRequest(BaseModel):
    dict_name: str