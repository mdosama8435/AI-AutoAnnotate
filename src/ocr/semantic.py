import google.generativeai as genai
import json
from PIL import Image
from typing import List
from ..models.core import OCRResult
from ..utils.config import settings
from ..utils.logger import log

class SemanticDetector:
    """Uses LLM Vision to semantically classify detected bounding boxes."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            log.warning("No Gemini API key. Semantic detection will use fallback types.")
            
    def classify_elements(self, image_path: str, ocr_result: OCRResult) -> OCRResult:
        """Takes an image and bounding boxes, returns classified elements."""
        if not self.api_key:
            return ocr_result
            
        log.info("Running Semantic Detection Engine...")
        
        boxes_data = [
            {"id": e.id, "box": [e.box.x_min, e.box.y_min, e.box.x_max, e.box.y_max]}
            for e in ocr_result.elements
        ]
        
        prompt = f"""
        You are a document analysis AI.
        Here are the bounding boxes detected in the attached educational image:
        {json.dumps(boxes_data)}
        
        For each box, identify its semantic type and transcribe the text inside it.
        Allowed types: "math_formula", "diagram", "mcq_option", "general_text".
        
        Return a JSON array where each object has:
        - "id": string (must match the input id)
        - "semantic_type": string
        - "text": string (the actual text or description of the diagram)
        """
        
        try:
            img = Image.open(image_path)
            response = self.model.generate_content([img, prompt])
            
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
                
            classifications = json.loads(result_text.strip())
            
            # Update the OCR elements with the LLM findings
            classification_map = {c["id"]: c for c in classifications}
            
            for element in ocr_result.elements:
                if element.id in classification_map:
                    data = classification_map[element.id]
                    element.semantic_type = data.get("semantic_type", "general_text")
                    element.text = data.get("text", element.text)
            
            log.info("Semantic classification successful.")
            return ocr_result
            
        except Exception as e:
            log.error(f"Semantic classification failed: {e}. Falling back to default.")
            return ocr_result
