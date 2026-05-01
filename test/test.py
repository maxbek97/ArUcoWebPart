import websocket
import base64
import cv2
import json
import time

ws = websocket.create_connection("ws://127.0.0.1:8000/api/ws")


frame_id = 0
# --- 1. INIT ---
camera_matrix = [
    [1000.0, 0.0, 640.0],
    [0.0, 1000.0, 360.0],
    [0.0, 0.0, 1.0]
]

dist_coeffs = [0, 0, 0, 0, 0]

marker_length = 0.05  # 5 см

ws.send(json.dumps({
    "type": "init",
    "camera_matrix": camera_matrix,
    "dist_coeffs": dist_coeffs,
    "marker_length": marker_length
}))
print("INIT RESPONSE:", ws.recv())

video_path = "./test/test3.mp4"  # замените на свой файл
cap = cv2.VideoCapture(video_path)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ресайз до безопасного размера, чтобы не было обрыва WS
    max_dim = 1080
    height, width = frame.shape[:2]
    if max(height, width) > max_dim:
        scale = max_dim / max(height, width)
        frame = cv2.resize(frame, (int(width*scale), int(height*scale)))

    # кодируем в base64
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode()

    # отправляем
    ws.send(json.dumps({
        "type": "frame",
        "frame_id": frame_id,
        "image": img_base64
    }))

    # принимаем ответ
    result = ws.recv()
    print(f"[FRAME {frame_id}] -> {result}")

    frame_id += 1
    time.sleep(0.03)  # ~30 fps

cap.release()
ws.close()

# img = cv2.imread("./test/test2.png")  # твой маркер
# _, buffer = cv2.imencode('.png', img)
# img_base64 = base64.b64encode(buffer).decode()
# for i in range(100):
#     ws.send(json.dumps({
#         "frame_id": 1,
#         "image": img_base64
#     }))

# result = ws.recv()
# print(result)