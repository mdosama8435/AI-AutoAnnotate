import cv2
import numpy as np
from typing import List, Tuple
from ..models.core import AnnotationAction
from .math_renderer import MathExpressionRenderer

class FrameRenderer:
    """Advanced renderer supporting dynamic, time-based annotations with persistence."""
    
    def __init__(self):
        self.colors = {
            "red": (0, 0, 255),
            "green": (0, 255, 0),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255),
            "magenta": (255, 0, 255),
            "cyan": (255, 255, 0),
            "black": (0, 0, 0),
            "white": (255, 255, 255)
        }
        self.math_renderer = MathExpressionRenderer()
        
        # State optimization
        self.last_t = -1.0
        self.canvas = None
        self.base_img = None
        
    def _get_color(self, color_name: str) -> Tuple[int, int, int]:
        return self.colors.get(color_name.lower(), (0, 0, 255))
        
    def render(self, base_image_path: str, actions: List[AnnotationAction], current_time: float) -> np.ndarray:
        """Renders active actions onto the frame, ensuring persistence of older strokes."""
        
        # Load base image on first frame
        if self.base_img is None or self.last_t > current_time:
            img = cv2.imread(base_image_path)
            if img is None:
                self.base_img = np.zeros((720, 1280, 3), dtype=np.uint8)
            else:
                self.base_img = img.copy()
            self.canvas = self.base_img.copy()
            self.last_t = 0.0

        img = self.base_img.copy()
        
        for action in actions:
            if current_time >= action.start_time:
                # Calculate progress [0.0 to 1.0]
                duration = action.end_time - action.start_time
                if duration <= 0:
                    progress = 1.0
                else:
                    progress = (current_time - action.start_time) / duration
                progress = min(max(progress, 0.0), 1.0)
                
                color_bgr = self._get_color(action.color)
                
                # --- Basic Types ---
                if action.action_type == "highlight" and action.target_box:
                    overlay = img.copy()
                    current_w = int(action.target_box.width * progress)
                    cv2.rectangle(
                        overlay,
                        (action.target_box.x_min, action.target_box.y_min),
                        (action.target_box.x_min + current_w, action.target_box.y_max),
                        color_bgr,
                        -1
                    )
                    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
                    
                elif action.action_type in ["rectangle", "box", "answer_box"] and action.target_box:
                    # Animate drawing the box
                    pts = [
                        (action.target_box.x_min, action.target_box.y_min),
                        (action.target_box.x_max, action.target_box.y_min),
                        (action.target_box.x_max, action.target_box.y_max),
                        (action.target_box.x_min, action.target_box.y_max),
                        (action.target_box.x_min, action.target_box.y_min)
                    ]
                    total_len = 4
                    drawn_len = total_len * progress
                    
                    for i in range(4):
                        if drawn_len > i:
                            p1 = pts[i]
                            p2 = pts[i+1]
                            seg_prog = min(1.0, drawn_len - i)
                            cur_p2 = (
                                int(p1[0] + (p2[0] - p1[0]) * seg_prog),
                                int(p1[1] + (p2[1] - p1[1]) * seg_prog)
                            )
                            cv2.line(img, p1, cur_p2, color_bgr, action.thickness)
                            
                elif action.action_type == "underline" and action.target_box:
                    y = action.target_box.y_max + 5
                    current_w = int(action.target_box.width * progress)
                    cv2.line(
                        img,
                        (action.target_box.x_min, y),
                        (action.target_box.x_min + current_w, y),
                        color_bgr,
                        action.thickness
                    )
                    
                elif action.action_type == "circle" and action.target_box:
                    center = action.target_box.center
                    radius = max(action.target_box.width, action.target_box.height) // 2 + 5
                    end_angle = int(360 * progress)
                    cv2.ellipse(
                        img, center, (radius, int(radius * 0.8)), 0, 0, end_angle, color_bgr, action.thickness
                    )
                    
                elif action.action_type == "arrow" and action.source_box and action.target_box:
                    pt1 = action.source_box.center
                    pt2 = action.target_box.center
                    cur_x = int(pt1[0] + (pt2[0] - pt1[0]) * progress)
                    cur_y = int(pt1[1] + (pt2[1] - pt1[1]) * progress)
                    cv2.arrowedLine(img, pt1, (cur_x, cur_y), color_bgr, action.thickness, tipLength=0.1)

                elif action.action_type in ["write_formula", "handwriting"] and action.text and action.target_box:
                    img = self.math_renderer.draw_formula(
                        img, action.text, 
                        action.target_box.x_min, action.target_box.y_min, 
                        color_bgr, progress=progress
                    )
                    
        self.last_t = current_time
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
