from app.models.DictionaryRequest import DictionaryRequest
from app.detector import set_dictionary
from app.repository import *
import app.state as state
from app.dict_map import DICT_MAP
from fastapi import APIRouter, HTTPException, Query
from psycopg2 import errors
import cv2
import re

router = APIRouter(prefix="/api/admin", tags=["admin"])




@router.get("/markers")
def read_markers():
    """Returns all markers from db"""
    try:
        return get_all_markers()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )
    

@router.get("/markers/{dictionary_name}/{marker_id}")
def read_one_marker(
    dictionary_name: str,
    marker_id: int
):
    """Returns chosen marker from db"""
    try:
        return get_marker(dictionary_name, marker_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )


@router.post("/markers")
def add_marker(marker_info: Marker_info):
    """Add a new marker info"""
    try:
        validate_marker(marker_info)
        return add_new_marker_info(marker_info)
    except HTTPException:
        raise
    except errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Marker with this dictionary and id already exists"
        )
    except errors.InvalidTextRepresentation as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid enum value: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )


@router.patch("/markers/")
def update_marker(
    marker_info: Marker_info,
    dictionary_name: str = Query(...),
    marker_id: int = Query(...),
):
    """Update marker info witch marker_id and dict_name"""
    try:
        if (
            marker_info.dictionary_name != dictionary_name or
            marker_info.marker_id != marker_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Path params and body must match"
            )
        validate_marker(marker_info)
        return update_marker_info(marker_info)
    except HTTPException:
        raise
    except errors.InvalidTextRepresentation:
        raise HTTPException(
            status_code=400,
            detail="Invalid enum value"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )
    

@router.delete("/markers/")
def detete_marker(
    dictionary_name: str = Query(...),
    marker_id: int = Query(...),
):
    """Delete marker from db"""
    try:
        return delete_marker(dictionary_name, marker_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )
    
    
def validate_marker(marker: Marker_info):
    if marker.dictionary_name not in DICT_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown dictionary '{marker.dictionary_name}'"
        )
    dict_type = DICT_MAP[marker.dictionary_name][0]
    max_markers = len(cv2.aruco.getPredefinedDictionary(dict_type).bytesList)

    if marker.marker_id < 0 or marker.marker_id >= max_markers:
        raise HTTPException(
            status_code=400,
            detail=f"marker_id must be between 0 and {max_markers - 1} for {marker.dictionary_name}"
        )
    
    if not isinstance(marker.payload, dict):
        raise HTTPException(
            status_code=400,
            detail="Payload must be a JSON object"
        )

    # 🔤 TEXT
    if marker.payload_type == "text":
        if set(marker.payload.keys()) != {"value"}:
            raise HTTPException(
                status_code=400,
                detail="Payload for 'text' must contain only 'value'"
            )

        value = marker.payload.get("value")

        if not isinstance(value, str):
            raise HTTPException(
                status_code=400,
                detail="'value' must be a string"
            )

        if len(value) > 255:
            raise HTTPException(
                status_code=400,
                detail="'value' must be <= 255 characters"
            )

    # 🤖 MODEL
    elif marker.payload_type == "model":
        if set(marker.payload.keys()) != {"src", "start_position"}:
            raise HTTPException(
                status_code=400,
                detail="Payload for 'model' must contain 'src' and 'start_position'"
            )

        src = marker.payload.get("src")
        pos = marker.payload.get("start_position")

        # src проверка
        if not isinstance(src, str):
            raise HTTPException(
                status_code=400,
                detail="'src' must be a string"
            )

        if not re.match(r"^[\w\-]+\.glb$", src):
            raise HTTPException(
                status_code=400,
                detail="'src' must be a valid .glb filename"
            )

        # start_position проверка
        if not isinstance(pos, list) or len(pos) != 3:
            raise HTTPException(
                status_code=400,
                detail="'start_position' must be an array of 3 numbers"
            )

        for coord in pos:
            if not isinstance(coord, (int, float)):
                raise HTTPException(
                    status_code=400,
                    detail="All coordinates in 'start_position' must be numbers"
                )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported payload_type '{marker.payload_type}'"
        )