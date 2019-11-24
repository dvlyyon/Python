import numpy as np
import cv2
import sys

fileName="vtest.mp4"
if len(sys.argv) == 2:
   fileName=sys.argv[1]
cap = cv2.VideoCapture(fileName)

print(cap.get(3))
print(cap.get(4))
print(cap.get(6))
while(cap.isOpened()):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame',gray)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

