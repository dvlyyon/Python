#!/usr/bin/python
import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('/home/david/Pictures/image8.jpg')

# Scaling : resize
cv2.imshow('image',img)
res = cv2.resize(img,None,fx=0.5,fy=0.5)
cv2.imshow('imageA',res)
cv2.waitKeyEx(0)
h,w = img.shape[:2]
res = cv2.resize(img,(w/2,h/2),interpolation = cv2.INTER_CUBIC)
cv2.imshow('imageA',res)
cv2.waitKey()
cv2.destroyAllWindows()

#Translation: change location
img = cv2.imread('/home/david/Pictures/image7.jpg')
rows, cols = img.shape[:2]
print (rows,cols)

M = np.float32([[1,0,100],[0,1,50]])
dst = cv2.warpAffine(img,M,(cols,rows))

cv2.imshow('img',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Rotation
# roate 60 degree
M = cv2.getRotationMatrix2D((cols/2,rows/2),15,1)
print ("type of Mask:" + str(type(M)))
dst = cv2.warpAffine(img,M,(cols,rows))
print ("type of image:" + str(type(dst)))
print (dst.shape)

cv2.imshow('img',dst)

pts1 = np.float32([[50,50],[200,50],[50,200]])
pts2 = np.float32([[10,100],[200,50],[100,250]])

M = cv2.getAffineTransform(pts1,pts2)

dst = cv2.warpAffine(img, M, (cols,rows))

cv2.imshow('imgAF',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

plt.subplot(121),plt.imshow(img),plt.title('Input')
plt.subplot(122),plt.imshow(dst),plt.title('Output')
plt.show()

img = cv2.imread('/home/david/Pictures/perspective1.jpg')
rows, cols, ch = img.shape

pts1 = np.float32([[143,438],[722,15],[143,591],[722,685]])
pts2 = np.float32([[0,0],[579,0],[0,670],[579,670]])

M = cv2.getPerspectiveTransform(pts1,pts2)
dst = cv2.warpPerspective(img,M,(670,579))

cv2.imshow('imageO',img)
cv2.imshow('imageA',dst)
cv2.waitKey(0)
cv2.destroyAllWindows();

plt.subplot(121),plt.imshow(img),plt.title('Input')
plt.subplot(122),plt.imshow(dst),plt.title('Output')
plt.show()

