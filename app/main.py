from fastapi import FastAPI, WebSocket, Body, WebSocketDisconnect
import base64
import numpy as np
import cv2
from app.models.DictionaryRequest import DictionaryRequest
from contextlib import asynccontextmanager
from app.detector import detect_markers, set_dictionary
from app.repository import load_payload_map

@asynccontextmanager
async def lifespan(app: FastAPI):
    global CURRENT_DICTIONARY, payload_map

    CURRENT_DICTIONARY = "DICT_4X4_50"
    payload_map = load_payload_map(CURRENT_DICTIONARY)
    set_dictionary(CURRENT_DICTIONARY)

    yield

app = FastAPI(lifespan=lifespan)

@app.websocket("/api/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    while True:
        try:
            data = await ws.receive_json()
            img_b64 = data.get("image")
            frame_id = data.get("frame_id")

            if img_b64 is None or frame_id is None:
                await ws.send_json({
                    "error": "Missing 'image' or 'frame_id'"
                })
                continue
            # decode image
            try:
                img_bytes = base64.b64decode(data["image"])
                np_arr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is None:
                        raise ValueError("Failed to decode image")
            except Exception as e:
                await ws.send_json({"error": f"Image decode error: {str(e)}"})
                continue
            try:
                markers = detect_markers(frame)
            except Exception as e:
                markers = []
                print(f"Detector error: {e}")
            # добавляем payload
            for m in markers:
                m["payload"] = payload_map.get(m["id"], {})

            await ws.send_json({
                "frame_id": data["frame_id"],
                "markers": markers
            })
        except WebSocketDisconnect:
            print("Client disconnected")
            break   # 🔥 ВАЖНО — выходим из цикла
        except Exception as e:
            print(f"WebSocket loop error: {e}")
            try:
                await ws.send_json({"error": str(e)})
            except:
                pass  # если ws уже закрыт
            



@app.post("/api/admin/switch-dictionary")
def switch_dictionary(req: DictionaryRequest):
    global CURRENT_DICTIONARY, payload_map

    dict_name = req.dict_name

    if dict_name not in ["DICT_4X4_50", "DICT_5X5_50"]:
        return {"status": "error", "message": f"Unknown dictionary '{dict_name}'"}

    try:
        payload_map = load_payload_map(dict_name)
        set_dictionary(dict_name)
        CURRENT_DICTIONARY = dict_name
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {
        "status": "ok",
        "current_dictionary": CURRENT_DICTIONARY,
        "markers_loaded": len(payload_map)
    }