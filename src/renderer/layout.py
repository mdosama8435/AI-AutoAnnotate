import cv2
import numpy as np

class LayoutEngine:
    def __init__(self):
        pass
        
    def find_workspace(self, image_path: str) -> tuple:
        """
        Analyzes the image and returns (start_x, start_y, width, height) 
        of the largest contiguous blank space to act as the whiteboard workspace.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return (50, 300, 400, 400)
            
        # Threshold: assuming black text on white background (presentation style)
        # We invert it: text becomes white (255), background becomes black (0)
        _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Dilate text to create larger connected components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        
        # Invert back: Text areas are 0, safe blank areas are 255
        safe_area = cv2.bitwise_not(dilated)
        
        # Find contours of safe areas
        contours, _ = cv2.findContours(safe_area, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_rect = (50, 300, 400, 400)
        max_area = 0
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Add padding to avoid writing right on the edge of text
            x += 20
            y += 20
            w -= 40
            h -= 40
            
            if w > 0 and h > 0:
                area = w * h
                if area > max_area:
                    max_area = area
                    best_rect = (x, y, w, h)
                    
        return best_rect
