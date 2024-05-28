import colorsys
import cv2
from PIL import ImageGrab
import numpy as np

def ps_map(window, map_region):
    left = window.left + map_region[0]
    top = window.top + map_region[1]
    width = map_region[2]
    height = map_region[3]

    bbox = (left, top, left + width, top + height)
    screenshot = np.array(ImageGrab.grab(bbox))
    img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return img

def detect_red_squares(image, min_area=1, max_area=100):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red_1 = np.array([2, 200, 200])
    upper_red_1 = np.array([2, 250, 250])

    mask = cv2.inRange(hsv, lower_red_1, upper_red_1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    red_squares = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            (x, y, w, h) = cv2.boundingRect(contour)
            center = (x + w // 2, y + h // 2)
            red_squares.append(center)
    return red_squares, mask