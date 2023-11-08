import os

import cv2

from src.detector import Detector

path = '../datas/images'

det = Detector()
for i in os.listdir(path):
    imgp = os.path.join(path, i)
    img = cv2.imread(imgp)
    det.detect2(img,)
