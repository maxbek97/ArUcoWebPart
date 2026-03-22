import cv2

aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
detector = cv2.aruco.ArucoDetector(aruco)

def detect_markers(frame):
    corners, ids, _ = detector.detectMarkers(frame)

    markers = []

    if ids is not None:
        for i in range(len(ids)):
            markers.append({
                "id": int(ids[i][0]),
                "corners": corners[i].tolist()
            })

    return markers