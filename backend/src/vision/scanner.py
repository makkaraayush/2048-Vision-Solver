import mss
import numpy as np
import cv2
from typing import Optional, Tuple

class GameScanner:
    def __init__(self):
        self.sct = mss.mss()
        self.grid_bounds: Optional[Tuple[int, int, int, int]] = None
        
    def locate_grid(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            if 0.95 <= aspect_ratio <= 1.05 and w > 250:
                self.grid_bounds = (x, y, w, h)
                return self.grid_bounds
        return None
