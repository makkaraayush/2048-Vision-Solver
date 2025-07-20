import mss
import numpy as np
import cv2
from typing import Optional, Tuple, List

TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

class GameScanner:
    def __init__(self):
        self.sct = mss.mss()
        self.grid_bounds: Optional[Tuple[int, int, int, int]] = None
        
    def locate_grid(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if 0.95 <= float(w)/h <= 1.05 and w > 250:
                self.grid_bounds = (x, y, w, h)
                return self.grid_bounds
        return None

    def get_tile_value(self, cell_crop: np.ndarray) -> int:
        h, w = cell_crop.shape[:2]
        center = cell_crop[h//4:3*h//4, w//4:3*w//4]
        avg_bgr = np.mean(center, axis=(0, 1))[:3]
        avg_rgb = (avg_bgr[2], avg_bgr[1], avg_bgr[0])
        
        best_val = 0
        min_dist = float('inf')
        for val, color in TILE_COLORS.items():
            dist = sum((a - b) ** 2 for a, b in zip(avg_rgb, color))
            if dist < min_dist:
                min_dist = dist
                best_val = val
        return best_val
