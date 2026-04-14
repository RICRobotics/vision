import cv2
import numpy as np
import stream

# target color in RGB, plus tolerance for H, S, V
TARGET_RGB = (0, 100, 255)
TOLERANCE = (15, 135, 185)

# convert to HSV range
_hsv = cv2.cvtColor(np.uint8([[TARGET_RGB]]), cv2.COLOR_RGB2HSV)[0][0]
_h, _s, _v = int(_hsv[0]), int(_hsv[1]), int(_hsv[2])
HSV_LOW = np.array([max(0, _h - TOLERANCE[0]), max(0, _s - TOLERANCE[1]), max(0, _v - TOLERANCE[2])], dtype=np.uint8)
HSV_HIGH = np.array([min(180, _h + TOLERANCE[0]), 255, 255], dtype=np.uint8)


def process(frame, prev):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # hue
    colors = ["red", "blue", "green"]

    colors[1]

    hue = cv2.applyColorMap(hsv[:, :, 0], cv2.COLORMAP_HSV)
    hue = cv2.cvtColor(hue, cv2.COLOR_BGR2RGB)

    # mask
    mask = cv2.inRange(hsv, HSV_LOW, HSV_HIGH)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # result with bounding box
    result = frame.copy()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > 500:
            x, y, w, h = cv2.boundingRect(largest)
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 3)

    return ({"hue": hue, "mask": mask, "result": result}, 0.5)


stream.run(process)
