#!/usr/bin/python

import cv2
# get all supported color space
flags = [i for i in dir(cv2) if i.startswith('COLOR_')]
print flags

# convert BGR space to HSV space
import numpy as np
green = np.uint8([[[0,255,0]]])
hsv_green = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
print hsv_green
hsv_green = cv2.cvtColor(green,cv2.COLOR_BGR2HSV_FULL)
print hsv_green
