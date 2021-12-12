import numpy as np
import cv2
import sys

fileName="vtest.mp4"
if len(sys.argv) == 2:
   fileName=sys.argv[1]
cap = cv2.VideoCapture(fileName)

print(f"fps: {cap.get(cv2.CAP_PROP_FPS)}")
print(f"width*height: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}*{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
print(cap.get(6))
timeout=5
while(cap.isOpened()):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame',gray)
    key = cv2.waitKey(timeout) 
    if key == ord('q'):
        break
    elif key == ord(']'):
        timeout += 5
    elif key == ord('['):
        timeout = 0 if timeout-5 < 0 else timeout-5
    elif key == ord('.'):
        timeout = 0

cap.release()
cv2.destroyAllWindows()

