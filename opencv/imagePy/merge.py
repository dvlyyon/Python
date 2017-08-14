#!/usr/bin/python

import numpy as np
import cv2

def nothing(x):
    pass

img1 = cv2.imread('/home/david/Pictures/image5.jpg')
img2 = cv2.imread('/home/david/Pictures/image10.jpg')

cv2.imshow('image5O',img1)
cv2.imshow('image10O', img2)

cv2.waitKey(0)
cv2.destroyAllWindows();


w1,h1,c1 = img1.shape;
w2,h2,c2 = img2.shape;

print (w1,h1,c1)
print (w2,h2,c2)

if w1 > w2: 
    w = w2
else: 
    w = w1
if h1 > h2: 
    h = h2
else: 
    h = h1

img1A = img1[0:w,0:h];
img2A = img2[0:w,0:h];
cv2.imshow('image5A',img1A)
cv2.imshow('image10A', img2A)
print (img1A.shape)

#cv2.waitKey(0)
#cv2.destroyAllWindows();

cv2.namedWindow('image')
cv2.createTrackbar('Image1','image',0,100,nothing)
#cv2.createTrackbar('Image2','image',0,100,nothing)

dst = cv2.addWeighted(img1A,100.0,img2A,0.0,0)

while(1):
    cv2.imshow('image',dst)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    m1 = cv2.getTrackbarPos('Image1','image')
    w1 = float(m1)/100
    w2 = float((100-m1))/100
    dst = cv2.addWeighted(img1A,w1,img2A,w2,0)
cv2.destroyAllWindows()
