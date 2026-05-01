import cv2
from app.dict_map import DICT_MAP


current_detector = None

def set_dictionary(dict_name: str):
    global current_detector

    if dict_name not in DICT_MAP:
        raise ValueError(f"Unknown dictionary {dict_name}")

    aruco_dict = cv2.aruco.getPredefinedDictionary(DICT_MAP[dict_name][0])
    current_detector = cv2.aruco.ArucoDetector(aruco_dict)


def detect_markers(frame):
    
    global current_detector
    if current_detector is None:
        raise Exception("Detector not initialized")
    
    corners, ids, _ = current_detector.detectMarkers(frame)

    markers = []

    if ids is not None:
        for i in range(len(ids)):
            markers.append({
                "id": int(ids[i][0]),
                "corners": corners[i].tolist()
            })

    return markers