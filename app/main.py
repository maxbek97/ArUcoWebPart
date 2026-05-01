from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import base64
import numpy as np
import cv2
from app.models.DictionaryRequest import DictionaryRequest
from contextlib import asynccontextmanager
from app.detector import detect_markers, set_dictionary
from app.repository import load_payload_map
import app.state as state
from app.routers import admin_dictionaries
from app.routers import admin_markers

@asynccontextmanager
async def lifespan(app: FastAPI):
    state.CURRENT_DICTIONARY = "DICT_4X4_50"
    state.payload_map = load_payload_map(state.CURRENT_DICTIONARY)
    set_dictionary(state.CURRENT_DICTIONARY)

    yield

app = FastAPI(lifespan=lifespan)
app.include_router(admin_dictionaries.router)
app.include_router(admin_markers.router)

@app.websocket("/api/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    camera_matrix = None
    dist_coeffs = None
    marker_length = None

    # print("Актуальный словарь " + state.CURRENT_DICTIONARY)

    while True:
        try:
            data = await ws.receive_json()
            msg_type = data.get("type")

            # --- INIT ---
            if msg_type == "init":
                try:
                    camera_matrix = np.array(data["camera_matrix"], dtype=np.float32)
                    dist_coeffs = np.array(data["dist_coeffs"], dtype=np.float32)
                    marker_length = float(data["marker_length"])

                    await ws.send_json({"status": "initialized"})
                except Exception as e:
                    await ws.send_json({"error": f"Init error: {str(e)}"})

                continue

            if msg_type == "frame":
                if camera_matrix is None:
                    await ws.send_json({"error": "Not initialized"})
                    continue

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


            markers = detect_markers(frame)
            for m in markers:
                corners = np.array(m["corners"], dtype=np.float32).reshape((1, 4, 2))

                try:
                    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                        corners,
                        marker_length,
                        camera_matrix,
                        dist_coeffs
                    )

                    m["rvec"] = rvecs[0][0].tolist()
                    m["tvec"] = tvecs[0][0].tolist()

                except Exception as e:
                    print(e)
                    m["rvec"] = None
                    m["tvec"] = None

                m["payload"] = state.payload_map.get(m["id"], {})

            await ws.send_json({
                "frame_id": data["frame_id"],
                "markers": markers
            })
        except WebSocketDisconnect:
            print("Client disconnected")
            break
        except Exception as e:
            print(f"WebSocket loop error: {e}")
            try:
                await ws.send_json({"error": str(e)})
            except:
                pass  # если ws уже закрыт