import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

class HandwritingRenderer:
    def __init__(self, font_path="src/assets/font.ttf", base_size=36):
        self.font_path = font_path
        self.base_size = base_size
        self._font_cache = {}
        
    def _get_font(self, size):
        if size not in self._font_cache:
            try:
                self._font_cache[size] = ImageFont.truetype(self.font_path, size)
            except IOError:
                # Fallback
                self._font_cache[size] = ImageFont.load_default()
        return self._font_cache[size]

    def draw_text(self, img_np: np.ndarray, text: str, x: int, y: int, color: tuple = (139, 0, 0), size: int = 36, progress: float = 1.0) -> np.ndarray:
        """
        Draws handwritten text onto an OpenCV image (numpy array).
        Uses progress (0.0 to 1.0) to reveal characters progressively left-to-right.
        Default color is dark blue.
        """
        if not text or progress <= 0:
            return img_np
            
        # Convert BGR (OpenCV) to RGB (PIL)
        img_pil = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        font = self._get_font(size)
        
        # Calculate how many characters to show based on progress
        char_count = max(1, int(len(text) * progress)) if progress < 1.0 else len(text)
        visible_text = text[:char_count]
        
        # PIL colors are RGB. The incoming color is BGR from OpenCV logic.
        r, g, b = color[2], color[1], color[0]
        
        draw.text((x, y), visible_text, font=font, fill=(r, g, b))
        
        # Convert back to BGR
        res_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return res_np

    def get_text_size(self, text: str, size: int = 36) -> tuple:
        """Returns (width, height) of the text block."""
        font = self._get_font(size)
        try:
            bbox = font.getbbox(text)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
        except AttributeError:
            # Fallback for older PIL versions
            w, h = font.getsize(text)
            return (w, h)
