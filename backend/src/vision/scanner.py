import mss
import numpy as np
import cv2

def crop_inner_tile(cell_crop: np.ndarray) -> np.ndarray:
    h, w = cell_crop.shape[:2]
    return cell_crop[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)]
