import io
import matplotlib.pyplot as plt
from matplotlib import rcParams
from PIL import Image
import numpy as np

# Configure matplotlib for mathtext
rcParams['text.usetex'] = False
rcParams['mathtext.fontset'] = 'cm' # Computer modern looks like textbook math

class MathExpressionRenderer:
    def __init__(self, font_size=24):
        self.font_size = font_size
        self._cache = {}
        
    def _render_latex_to_rgba(self, formula: str, color: str = 'black') -> np.ndarray:
        cache_key = f"{formula}_{color}_{self.font_size}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, f"${formula}$", fontsize=self.font_size, color=color)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent=True, dpi=105, bbox_inches='tight', pad_inches=0.0)
        plt.close(fig)
        
        buf.seek(0)
        img_pil = Image.open(buf).convert("RGBA")
        img_np = np.array(img_pil)
        
        self._cache[cache_key] = img_np
        return img_np
        
    def draw_formula(self, bg_img: np.ndarray, formula: str, x: int, y: int, color: tuple, progress: float) -> np.ndarray:
        """Draws the LaTeX formula progressively based on progress (0 to 1.0)."""
        if progress <= 0:
            return bg_img
            
        # OpenCV uses BGR, convert requested color to matplotlib hex
        r, g, b = color[2], color[1], color[0]
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        rgba_latex = self._render_latex_to_rgba(formula, hex_color)
        
        h, w, _ = rgba_latex.shape
        
        # Determine how much of the width to show
        show_w = int(w * progress)
        if show_w == 0:
            return bg_img
            
        rgba_latex = rgba_latex[:, :show_w, :]
        
        # Composite onto background
        y1, y2 = y, y + h
        x1, x2 = x, x + show_w
        
        # Ensure bounds
        if y1 >= bg_img.shape[0] or x1 >= bg_img.shape[1]:
            return bg_img
            
        y2 = min(y2, bg_img.shape[0])
        x2 = min(x2, bg_img.shape[1])
        
        # Recalculate slice in case of boundary crop
        rgba_latex = rgba_latex[:y2-y1, :x2-x1, :]
        
        alpha_mask = rgba_latex[:, :, 3] / 255.0
        
        # rgba_latex is RGB, bg_img is BGR
        bg_img[y1:y2, x1:x2, 0] = (
            alpha_mask * rgba_latex[:, :, 2] +
            (1.0 - alpha_mask) * bg_img[y1:y2, x1:x2, 0]
        )
        bg_img[y1:y2, x1:x2, 1] = (
            alpha_mask * rgba_latex[:, :, 1] +
            (1.0 - alpha_mask) * bg_img[y1:y2, x1:x2, 1]
        )
        bg_img[y1:y2, x1:x2, 2] = (
            alpha_mask * rgba_latex[:, :, 0] +
            (1.0 - alpha_mask) * bg_img[y1:y2, x1:x2, 2]
        )
            
        return bg_img
