from app.models.Marker_info import MarkerForm, MarkerInfoDTO
from app.detector import set_dictionary
from app.repository import *
from app.service import *
import app.state as state
from app.dict_map import DICT_MAP
from fastapi import APIRouter, HTTPException, Query
from psycopg2 import errors
import cv2
import re
from fastapi import Depends, UploadFile, File
import json

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
        marker = get_marker(dictionary_name, marker_id)
        if marker is None:
            raise HTTPException(
        status_code=404,
        detail="Marker not found"
    )
        return marker
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )


@router.post("/markers")
async def add_marker(
    form: MarkerForm= Depends(),
    file: UploadFile = File(None)
):
    """Add a new marker info"""
    try:
        try:
            payload_dict = json.loads(form.payload)
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON in payload")
        marker_info = MarkerInfoDTO(
            dictionary_name=form.dictionary_name,
            marker_id=form.marker_id,
            payload_type=form.payload_type,
            payload=payload_dict
            )

        validate_marker(marker_info)

        if marker_info.payload_type == "text":
            return add_new_marker_info(marker_info)
        

        saved_filename = None

        if file is None:
            raise HTTPException(400, "File is required for model")
        
        try:
            saved_filename = save_model_file(file)
            marker_info.payload["src"] = saved_filename
            result = add_new_marker_info(marker_info)
            return result
        except Exception:
            delete_model_file(saved_filename)
            raise

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
    form: MarkerForm = Depends(),
    file: UploadFile = File(None),
    dictionary_name: str = Query(...),
    marker_id: int = Query(...),
):
    """Update marker info witch marker_id and dict_name"""
    try:
        try:
            payload_dict = json.loads(form.payload)
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON in payload")
        marker_info = MarkerInfoDTO(
            dictionary_name=form.dictionary_name,
            marker_id=form.marker_id,
            payload_type=form.payload_type,
            payload=payload_dict
        )

        if (
            marker_info.dictionary_name != dictionary_name or
            marker_info.marker_id != marker_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Path params and body must match"
            )
        
                # 🔍 получаем старый маркер
        old_marker = get_marker(dictionary_name, marker_id)
        if old_marker is None:
            raise HTTPException(404, "Marker not found")
        
        validate_marker(marker_info)


        # =========================
        # 🧠 ЛОГИКА ОБНОВЛЕНИЯ
        # =========================

        # 1. TEXT
        if marker_info.payload_type == "text":
            if file is not None:
                raise HTTPException(400, "File is not allowed for text payload")
            updated = update_marker_info(marker_info)
            if updated is None:
                raise HTTPException(
                    status_code=404,
                    detail="Marker not found"
                )
            # если раньше была модель — удаляем файл
            if old_marker.payload_type == "model":
                old_filename = old_marker.payload.get("src")
                delete_model_file(old_filename)


            return updated 
        
        # 2. Модель
        if marker_info.payload_type == "model":

            if file is None:
                raise HTTPException(400, "File is required for model")
            
            saved_filename = save_model_file(file)
            marker_info.payload["src"] = saved_filename

            try:
                updated = update_marker_info(marker_info)
                if updated is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Marker not found"
                    )

                # если раньше была модель — удалить старый файл
                if old_marker.payload_type == "model":
                    old_filename = old_marker.payload.get("src")

                    if old_filename != saved_filename:
                        delete_model_file(old_filename)

                return updated

            except Exception:
                # если БД упала — удаляем новый файл
                delete_model_file(saved_filename)
                raise

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
        deleted = delete_marker(dictionary_name, marker_id)
        if not deleted:
            raise HTTPException(404, "Marker not found")
        
                # если модель — удаляем файл
        if deleted.payload_type == "model":
            filename = deleted.payload.get("src")
            if filename:
                delete_model_file(filename)

        return {
            "message": f"Marker {marker_id} from {dictionary_name} deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown server error '{str(e)}'"
        )