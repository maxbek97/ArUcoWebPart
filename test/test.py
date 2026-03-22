import websocket
import base64
import cv2
import json

ws = websocket.create_connection("ws://127.0.0.1:8000/ws")

img = cv2.imread("./test/test.jpg")  # твой маркер

_, buffer = cv2.imencode('.jpg', img)
img_base64 = base64.b64encode(buffer).decode()

ws.send(json.dumps({
    "frame_id": 1,
    "image": img_base64
}))

result = ws.recv()
print(result)