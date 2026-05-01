from app.models.DictionaryRequest import DictionaryRequest
from app.detector import set_dictionary
from app.repository import *
import app.state as state
from app.dict_map import DICT_MAP
from fastapi import APIRouter, HTTPException, Query
from psycopg2 import errors
from app.service import download_model_file, calculate_models_hash

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/switch-dictionary")
def switch_dictionary(req: DictionaryRequest):
    """Switch active dictionary detector"""
    dict_name = req.dict_name
    
    if dict_name not in DICT_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown dictionary '{dict_name}'"
        )

    try:

        set_dictionary(dict_name)
        state.payload_map = load_payload_map(dict_name)
        state.CURRENT_DICTIONARY = dict_name
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )

    return {
        "current_dictionary": state.CURRENT_DICTIONARY,
        "markers_loaded": len(state.payload_map),
        "models_hash": calculate_models_hash(state.CURRENT_DICTIONARY)
    }

@router.get("/dictionaries")
def get_dictionaries():
    """Return list of dictionaries"""
    try:
        return {"current_dict": state.CURRENT_DICTIONARY,
                "dict_names" : [dictionary for dictionary in DICT_MAP.keys()],
                "models_hash": calculate_models_hash(state.CURRENT_DICTIONARY)
                }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )
    
@router.get("/dictionaries/{dict_name}/models")
def get_dictionary_models(dict_name: str):
    """Return list of names model files by them dictionary name"""

    if dict_name not in DICT_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown dictionary '{dict_name}'"
        )
    markers = get_all_markers(dict_name)

    return [ m.payload["src"]
        for m in markers
        if m.payload_type == "model"
    ]

@router.get("/models/{filename}")
def download_model(filename: str):
    """Downloads file from server"""
    return download_model_file(filename)
