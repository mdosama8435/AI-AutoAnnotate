import cv2
import numpy as np
from PIL import Image
from typing import List
from ..models.core import OCRResult, OCRElement, BoundingBox
from ..utils.logger import log
from ..utils.errors import OCRProcessingError

class OCRDetector:
    """Detects text and equations in images using OpenCV."""
    
    def __init__(self):
        log.info("Initialized OCRDetector")
        
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for contour detection."""
        img = cv2.imread(image_path)
        if img is None:
            raise OCRProcessingError(f"Could not read image: {image_path}")
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding to handle different lighting
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Dilation to connect text characters into blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        return img, dilated

    def extract_elements(self, image_path: str) -> OCRResult:
        """Extract bounding boxes of text/equations from the image."""
        try:
            img, dilated = self._preprocess_image(image_path)
            height, width = img.shape[:2]
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            elements = []
            for i, c in enumerate(contours):
                x, y, w, h = cv2.boundingRect(c)
                
                # Filter out very small boxes (noise)
                if w > 20 and h > 10:
                    # In a full implementation, we might pass the cropped region to an OCR engine/Gemini here.
                    # For this platform, we detect the regions to allow the LLM to target them.
                    box = BoundingBox(x_min=x, y_min=y, x_max=x+w, y_max=y+h)
                    
                    # Dummy text for now; we rely on LLM planner to map transcript to these boxes based on relative position
                    # Or we could use Gemini on the whole image to extract text with bounding boxes.
                    element = OCRElement(
                        id=f"region_{i}",
                        text=f"Region {i}",
                        box=box,
                        semantic_type="general_text"
                    )
                    elements.append(element)
                    
            # Sort elements top-to-bottom, left-to-right
            elements.sort(key=lambda e: (e.box.y_min, e.box.x_min))
            
            log.info(f"Detected {len(elements)} OCR elements in {image_path}")
            return OCRResult(elements=elements, image_width=width, image_height=height)
            
        except Exception as e:
            log.error(f"OCR processing failed: {e}")
            raise OCRProcessingError(f"Failed to process image: {e}")
