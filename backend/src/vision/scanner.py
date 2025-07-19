import mss
import numpy as np
import cv2

class GameScanner:
    def __init__(self):
        self.sct = mss.mss()
        
    def capture_screen(self) -> np.ndarray:
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        return np.array(screenshot)
