import cv2

aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

img = cv2.aruco.generateImageMarker(aruco, 2, 300)
cv2.imwrite("marker_2.png", img)