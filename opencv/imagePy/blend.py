
import numpy as np
import cv2

def nothing(x):
    pass

#make sure img2.width < img1.width and img2.height < img1.height
img1 = cv2.imread('images/image8.jpg')
img2 = cv2.imread('images/image11.jpg')

cv2.imshow('image5O',img1)
cv2.imshow('image10O', img2)

cv2.waitKey(0)
cv2.destroyAllWindows();


w1,h1,c1 = img1.shape;
w2,h2,c2 = img2.shape;
print (w1,h1,c1)
print (w2,h2,c2)

roi = img1[0:w2,0:h2]
# Now create a mask of logo and create its inverse mask also
img2gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
print (img2gray.shape)
cv2.imshow('imagwGray',img2gray)
cv2.waitKey(0)
cv2.destroyAllWindows();
ret, mask = cv2.threshold(img2gray, 10,255, cv2.THRESH_BINARY)
mask_inv = cv2.bitwise_not(mask)

# Now black-out the area of logo in ROI
img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
# Take only region of logo from logo image.
img2_fg = cv2.bitwise_and(img2,img2,mask = mask)
cv2.imshow('imag2bg',img1_bg)
cv2.imshow('imag2fg',img2_fg)
cv2.waitKey(0)
cv2.destroyAllWindows();

# Put logo in ROI and modify the main image
dst = cv2.add(img1_bg,img2_fg)
img1[0:w2, 0:h2] = dst
cv2.namedWindow('image',cv2.WINDOW_NORMAL)
cv2.imshow('image',img1)

import smooth
dst1 = smooth.smoothAverage(img1)
dst2 = smooth.smoothGaussian(img1)
dst3 = smooth.smoothMedian(img1)
dst4 = smooth.smoothBilateral(img1)

from matplotlib import pyplot as plt

plt.subplot(231),plt.imshow(img1),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(232),plt.imshow(dst1),plt.title('Average')
plt.xticks([]), plt.yticks([])
plt.subplot(233),plt.imshow(dst2),plt.title('Gaussian')
plt.xticks([]), plt.yticks([])
plt.subplot(234),plt.imshow(dst3),plt.title('Median')
plt.xticks([]), plt.yticks([])
plt.subplot(235),plt.imshow(dst4),plt.title('Bilateral')
plt.xticks([]), plt.yticks([])
plt.show()

cv2.imshow('image1',dst1[0:w2+50,0:h2+50])
cv2.imshow('image2',dst2[0:w2+50,0:h2+50])
cv2.imshow('image3',dst3[0:w2+50,0:h2+50])
cv2.imshow('image4',dst4[0:w2+50,0:h2+50])

cv2.waitKey(0)
cv2.destroyAllWindows()
