from fastapi import FastAPI, WebSocket
import base64
import numpy as np
import cv2

from app.detector import detect_markers
from app.payload import payload_map

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    while True:
        data = await ws.receive_json()

        # decode image
        img_bytes = base64.b64decode(data["image"])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        markers = detect_markers(frame)

        # добавляем payload
        for m in markers:
            m["payload"] = payload_map.get(m["id"], {})

        await ws.send_json({
            "frame_id": data["frame_id"],
            "markers": markers
        })