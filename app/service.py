from app.models.Marker_info import MarkerInfoDTO
from app.repository import *
from app.dict_map import DICT_MAP
from fastapi import HTTPException
import cv2
from fastapi import UploadFile
import uuid

UPLOAD_DIR = "storage/models"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_marker(marker: MarkerInfoDTO):
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
        
        if len(value) == 0:
            raise HTTPException(
                status_code=400,
                detail="'value' must be not empty"
            )

    # 🤖 MODEL
    elif marker.payload_type == "model":
        if set(marker.payload.keys()) != {"start_position"}:
            raise HTTPException(
                status_code=400,
                detail="Payload for 'model' must contain only 'start_position'"
            )

        pos = marker.payload.get("start_position")

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
    

def sanitize_filename(filename: str) -> str:
    # убираем путь если кто-то прислал "C:\fakepath\model.glb"
    base = os.path.basename(filename)

    # убираем опасные символы
    base = base.replace(" ", "_")

    return base

def save_model_file(file: UploadFile) -> str:
    if file is None:
        raise HTTPException(400, "File is required")

    if not file.filename:
        raise HTTPException(400, "Empty filename")

    filename = sanitize_filename(file.filename)

    # защита от перезаписи (очень важно)
    name, ext = os.path.splitext(filename)

    if ext.lower() != ".glb":
        raise HTTPException(400, "Only .glb files allowed")

    # если такой файл уже есть — добавляем uuid
    file_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(file_path):
        filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename


def delete_model_file(filename: str) -> None:
    if not filename:
        return
    
    safe_filename = sanitize_filename(filename)

    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    if os.path.exists(file_path):
        os.remove(file_path)