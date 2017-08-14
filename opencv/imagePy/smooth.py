#!/usr/bin/python

import cv2
import numpy as np

def smoothAverage(img,row=3,col=3):
    return cv2.blur(img,(row,col))

def smoothGaussian(img,row=3,col=3):
    return cv2.GaussianBlur(img,(row,col),0)

def smoothMedian(img,size=3):
    return cv2.medianBlur(img,size)

def smoothBilateral(img,d=6,color=75,colorSpace=75):
    return cv2.bilateralFilter(img,d,color,colorSpace)
