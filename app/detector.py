import cv2

ARUCO_DICTS = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
}

current_detector = None

def set_dictionary(dict_name: str):
    global current_detector

    if dict_name not in ARUCO_DICTS:
        raise ValueError(f"Unknown dictionary {dict_name}")

    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICTS[dict_name])
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