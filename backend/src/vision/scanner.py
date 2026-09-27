import cv2
import numpy as np
import mss
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

class BoardScanner:
    def __init__(self):
        self.sct = mss.mss()
        self.board_bbox: Optional[dict] = None
        self.manual_calibrated: bool = False
        
        # Color definitions for 2048 tiles (standard colors)
        # Using BGR format for OpenCV
        self.tile_colors = {
            0: (180, 193, 205), # Empty tile color
            -1: (160, 173, 187), # Board background color (mapped to 0)
            2: (218, 228, 238),
            4: (200, 224, 237),
            8: (121, 177, 242),
            16: (99, 149, 245),
            32: (95, 124, 246),
            64: (59, 94, 246),
            128: (114, 207, 237),
            256: (97, 204, 237),
            512: (80, 200, 237),
            1024: (61, 197, 237),
            2048: (46, 194, 237)
        }

    def set_manual_bbox(self, bbox: dict):
        """Sets an exact user-calibrated bounding box and locks it."""
        self.board_bbox = bbox
        self.manual_calibrated = True
        logger.info(f"Manual board calibration applied: {self.board_bbox}")

    def reset_calibration(self):
        """Resets manual calibration and reverts to auto-detection."""
        self.manual_calibrated = False
        self.board_bbox = None
        logger.info("Board calibration reset to automatic detection.")

    def capture_screen(self) -> np.ndarray:
        # monitor[0] captures ALL monitors, so it works no matter which screen the game is on
        monitor = self.sct.monitors[0]
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        # Fix OpenCV syntax: COLOR_BGRA2BGR is the correct constant
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
    def find_board(self, img: np.ndarray) -> bool:
        """
        Attempts to locate the 2048 game board on screen.
        If the board was manually calibrated, preserves the calibrated bounding box.
        Otherwise scans contours, prioritizing candidates containing the 2048 board background color.
        """
        if self.manual_calibrated and self.board_bbox is not None:
            return True

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        
        # Use RETR_TREE or RETR_LIST because RETR_EXTERNAL will only find the monitor/browser edges!
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        best_board = None
        max_area = 0
        best_color_board = None
        best_color_area = 0

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.05 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                area = w * h
                # Check aspect ratio (square) and minimum size (relaxed to 180px for scaled windows)
                if 0.85 < w / h < 1.15 and w > 180:
                    crop = img[y:y+h, x:x+w]
                    # Check for 2048 grid background (#bbada0) and tile tones:
                    # B: 135-200, G: 150-215, R: 165-230
                    mask = cv2.inRange(crop, np.array([135, 150, 165]), np.array([200, 215, 230]))
                    match_ratio = np.count_nonzero(mask) / float(area) if area > 0 else 0
                    
                    if match_ratio > 0.15:
                        if area > best_color_area:
                            best_color_area = area
                            best_color_board = {"top": y, "left": x, "width": w, "height": h}

                    if area > max_area:
                        max_area = area
                        best_board = {"top": y, "left": x, "width": w, "height": h}
                        
        selected_board = best_color_board or best_board
        if selected_board:
            self.board_bbox = selected_board
            logger.info(f"Found board at {self.board_bbox} (color_matched: {best_color_board is not None})")
            return True
            
        return False

    def extract_grid(self, frame: Optional[np.ndarray] = None) -> Tuple[int, ...]:
        """Extracts the 4x4 grid values from the current screen."""
        if frame is None:
            frame = self.capture_screen()
            
        if self.board_bbox is None:
            if not self.find_board(frame):
                raise ValueError("Could not locate 2048 board on screen.")
                
        # Crop to board
        x, y, w, h = self.board_bbox['left'], self.board_bbox['top'], self.board_bbox['width'], self.board_bbox['height']
        board_img = frame[y:y+h, x:x+w]
        
        # Split into 4x4
        cell_w = w // 4
        cell_h = h // 4
        
        grid = []
        for row in range(4):
            for col in range(4):
                cx1 = col * cell_w
                cy1 = row * cell_h
                cx2 = cx1 + cell_w
                cy2 = cy1 + cell_h
                
                cell_img = board_img[cy1:cy2, cx1:cx2]
                val = self._detect_tile_value(cell_img)
                grid.append(val)
                
        return tuple(grid)

    def _detect_tile_value(self, cell_img: np.ndarray) -> int:
        """
        Determines tile value based on calibrated background color sampling
        and digit count / saturation validation for yellow tiles (128 vs 256 vs 512).
        """
        h, w = cell_img.shape[:2]
        
        # Sample the top-center safe patch (y: 16%-28%, x: 35%-65%).
        # This completely avoids numbers (drawn in the center) and borders/rounded corners/gaps.
        y1, y2 = int(h * 0.16), int(h * 0.28)
        x1, x2 = int(w * 0.35), int(w * 0.65)
        patch = cell_img[y1:y2, x1:x2]
        if patch.size == 0:
            return 0
            
        bg_color = np.median(patch, axis=(0, 1))
        
        min_dist = float('inf')
        best_val = 0
        
        for val, color in self.tile_colors.items():
            dist = np.linalg.norm(bg_color - np.array(color))
            if dist < min_dist:
                min_dist = dist
                best_val = val
                
        # Yellow family disambiguation (128, 256, 512, 1024, 2048)
        # In 2048, yellow/gold tiles share similar hues.
        # We use high-contrast Blue-channel white text extraction combined with
        # a foolproof multi-feature voting ensemble:
        # 1. Topology / Hole count (RETR_CCOMP):
        #    '128' has digit '8' (2 loops -> 2 holes)
        #    '256' has digit '6' (1 loop -> 1 hole)
        #    '512' has digits '5','1','2' (0 loops -> 0 holes)
        #    '2048' has digits '0' and '8' (at least 3 holes)
        #    '1024' has digit '0' (at most 2 holes)
        # 2. Left vs Right Ink balance:
        #    In '128', left digit '1' is light while right digit '8' is dense (ink_ratio <= 0.77).
        #    In '256', left digit '2' and right digit '6' have equal weight (ink_ratio >= 0.82).
        # 3. Digit 0 vs Digit 1 width ratio:
        #    In '128', '1' is narrower than '2' (w0/w1 < 0.88).
        #    In '256', '2' has same width as '5' (w0/w1 >= 0.95).
        # 4. Calibrated background color evidence.
        if best_val in (128, 256, 512, 1024, 2048):
            b, g, r = float(bg_color[0]), float(bg_color[1]), float(bg_color[2])
            hsv_patch = cv2.cvtColor(np.uint8([[bg_color]]), cv2.COLOR_BGR2HSV)[0][0]
            sat = int(hsv_patch[1])
            
            # White text has Blue >= 235, while yellow bg has Blue <= 120.
            # Dynamic blue threshold isolates white text with zero background bleed:
            thresh_val = max(130.0, b + (242.0 - b) * 0.35)
            roi = cell_img[int(h * 0.22):int(h * 0.78), int(w * 0.08):int(w * 0.92)]
            mask = (roi[:, :, 0] > thresh_val).astype(np.uint8) * 255
            
            # Count loops/holes in text using 2-level contour hierarchy (RETR_CCOMP)
            cnts, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            min_hole = max(6.0, (h * w) * 0.0012)
            holes = 0
            external_cnts = []
            if hierarchy is not None:
                for i, h_info in enumerate(hierarchy[0]):
                    area = cv2.contourArea(cnts[i])
                    if h_info[3] != -1:  # Child contour is a hole
                        if area >= min_hole:
                            holes += 1
                    else:  # External contour is a digit
                        if area >= max(12.0, (h * w) * 0.002):
                            external_cnts.append(cnts[i])
                            
            digit_cnts = sorted(external_cnts, key=lambda c: cv2.boundingRect(c)[0])
            num_digits = len(digit_cnts)
            boxes = [cv2.boundingRect(c) for c in digit_cnts]
            
            first_ratio = (boxes[0][2] / float(boxes[0][3])) if len(boxes) >= 1 else 0.55
            w0_w1 = (boxes[0][2] / float(boxes[1][2])) if len(boxes) >= 2 else 1.0
            
            # Compute Left vs Right ink ratio across text bounding box
            if len(boxes) > 0:
                x_min = min(bx[0] for bx in boxes)
                x_max = max(bx[0] + bx[2] for bx in boxes)
                y_min = min(bx[1] for bx in boxes)
                y_max = max(bx[1] + bx[3] for bx in boxes)
                text_crop = mask[y_min:y_max, x_min:x_max]
                mid_x = text_crop.shape[1] // 2
                left_ink = np.count_nonzero(text_crop[:, :mid_x])
                right_ink = np.count_nonzero(text_crop[:, mid_x:])
                ink_ratio = left_ink / float(max(right_ink, 1))
            else:
                ink_ratio = 0.8
                
            # Disambiguate 1024 vs 2048:
            is_4_digit = (num_digits >= 4) or (best_val in (1024, 2048) and b <= 74)
            if is_4_digit or (b <= 68 and sat >= 188):
                if holes >= 3:
                    return 2048
                elif holes <= 2 and (first_ratio < 0.52 or w0_w1 < 0.85 or b >= 55):
                    return 1024
                elif first_ratio < 0.52 or w0_w1 < 0.85:
                    return 1024
                elif b >= 55:
                    return 1024
                else:
                    return 2048
                    
            # Unified 3-way voting for 128 vs 256 vs 512:
            # 128: digits '1','2','8' -> '8' has 2 holes; digit 0 is '1' (slender); right-heavy ink
            # 256: digits '2','5','6' -> '6' has 1 hole; no '1' (all digits wide); balanced ink
            # 512: digits '5','1','2' -> 0 holes; digit 1 is '1' (slender); balanced ink
            v_128, v_256, v_512 = 0, 0, 0
            
            # 1. Topology / Holes:
            if holes >= 2:
                v_128 += 6
            elif holes == 1:
                v_256 += 6
            elif holes == 0:
                v_512 += 6
                
            # 2. Digit position & width of '1':
            if len(boxes) >= 3:
                w0, w1, w2 = boxes[0][2], boxes[1][2], boxes[2][2]
                if w0 < w1 * 0.88 and w0 < w2 * 0.88:
                    v_128 += 4
                elif w1 < w0 * 0.88 and w1 < w2 * 0.88:
                    v_512 += 4
                elif abs(w0 - w1) <= 2 and abs(w1 - w2) <= 2:
                    v_256 += 3
            elif len(boxes) == 2:
                w0, w1 = boxes[0][2], boxes[1][2]
                if w0 < w1 * 0.85:
                    v_128 += 3
                elif w1 < w0 * 0.85:
                    v_512 += 3
                    
            # 3. Ink balance (128 is strongly right-heavy due to '8')
            if ink_ratio <= 0.77:
                v_128 += 3
            elif ink_ratio >= 0.80:
                v_256 += 1
                v_512 += 1
                
            # 4. Color sampling evidence:
            if b >= 106:
                v_128 += 3
            elif b <= 88:
                v_512 += 3
            elif 90 <= b <= 104:
                v_256 += 3
                
            if best_val == 128:
                v_128 += 2
            elif best_val == 256:
                v_256 += 2
            elif best_val == 512:
                v_512 += 2
                
            scores = {128: v_128, 256: v_256, 512: v_512}
            return max(scores, key=scores.get)
                
        return 0 if best_val == -1 else best_val
