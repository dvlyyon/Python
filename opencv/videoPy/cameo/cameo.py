import sys
import time
import cv2
from managers import WindowManager, CaptureManager

class Cameo(object):

    def __init__(self, cap, mirror=False):
        self._windowManager = WindowManager('Cameo',
                                            self.onKeypress)
        self._captureManager = CaptureManager(
            cap, self._windowManager, mirror)
        self.timeout = 0
        self.pause = False

    def run(self):
        """Run the main loop."""
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            if not self.pause:
                self._captureManager.enterFrame()
                frame = self._captureManager.frame

                if frame is not None:
                    pass

                time.sleep(self.timeout)
                self._captureManager.exitFrame()
            self._windowManager.processEvents()

    def onKeypress(self, keycode):
        """Handle a keypress.

        space  -> Take a screenshot.
        tab    -> Start/stop recording a screencast.
        escape -> Quit.

        """
        if keycode == ord('s'): # space
            self._captureManager.writeImage('screenshot.png')
        elif keycode == ord(' '):
            self.pause = not self.pause
        elif keycode == ord('c'):
            self._captureManager.toggleColor()
        elif keycode == 9: # tab
            if not self._captureManager.isWritingVideo:
                self._captureManager.startWritingVideo(
                    'screencast.avi')
            else:
                self._captureManager.stopWritingVideo()
        elif keycode == ord(']'):
            self.timeout += 0.001
            print(f"timeout:{self.timeout}")
        elif keycode == ord('['):
            self.timeout = 0 if self.timeout < 0.001 else self.timeout - 0.001
            print(f"timeout:{self.timeout}")
        elif keycode == 27 or keycode == ord('q'): # escape
            self._windowManager.destroyWindow()

if __name__=="__main__":
    mirror = False
    if len(sys.argv) == 2:
        fileName=sys.argv[1]
        cap = cv2.VideoCapture(fileName)
    else:
        cap = cv2.VideoCapture(0)
        mirror = True
    myCameo = Cameo(cap,mirror)
    myCameo.run()
