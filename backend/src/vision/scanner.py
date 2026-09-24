import mss
import numpy as np
import cv2

def sample_top_center(crop: np.ndarray):
    h, w = crop.shape[:2]
    patch = crop[int(h*0.12):int(h*0.28), int(w*0.35):int(w*0.65)]
    avg = np.mean(patch, axis=(0, 1))
    return int(avg[2]), int(avg[1]), int(avg[0])
