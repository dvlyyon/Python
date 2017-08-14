#!/usr/bin/python

import cv2
import numpy as np

img = cv2.imread('/home/david/Pictures/blend.png')

# mouse callback function
def selectPixel(event,x,y,flags,image):

    if event == cv2.EVENT_LBUTTONDBLCLK:
        print (x,y)
        print (image[y,x])

# Create a black image, a window and bind the function to window
def selectPixelFromImage(img):
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', selectPixel, param = img)
    while(1):
        cv2.imshow('image',img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('m'):
            mode = not mode
        elif k == 27:
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    file_name = '/home/david/Pictures/blend.png'
    import sys
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    print ("file name:"+file_name)
    img = cv2.imread(file_name)
    selectPixelFromImage(img)
