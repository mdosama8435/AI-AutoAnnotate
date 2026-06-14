import json
import google.generativeai as genai
from typing import List, Dict, Any
from ..models.core import Transcript, OCRResult, AnnotationAction, Timeline
from ..utils.config import settings
from ..utils.logger import log
from ..utils.errors import LLMProcessingError

class AnnotationPlanner:
    """Uses LLM to map transcript segments to OCR regions and generate drawing actions."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            log.warning("Gemini API key is not set. Planner will fail if called.")
        else:
            genai.configure(api_key=self.api_key)
            # Using 1.5 Pro for complex reasoning
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            log.info("AnnotationPlanner initialized with Gemini 1.5 Pro")

    def generate_timeline(self, transcript: Transcript, ocr: OCRResult) -> Timeline:
        """Generates a Timeline of AnnotationActions based on audio and image regions."""
        if not self.api_key:
            raise LLMProcessingError("Gemini API key is not configured.")
            
        log.info("Generating annotation timeline via LLM...")
        
        # Prepare context for the prompt
        transcript_data = [
            {"id": s.id, "text": s.text, "start": s.start, "end": s.end} 
            for s in transcript.segments
        ]
        
        ocr_data = [
            {
                "region_id": i, 
                "text": e.text, 
                "box": {"xmin": e.box.x_min, "ymin": e.box.y_min, "xmax": e.box.x_max, "ymax": e.box.y_max}
            }
            for i, e in enumerate(ocr.elements)
        ]
        
        prompt = f"""
        You are an expert educational video director. You have:
        1. A transcript of a teacher speaking.
        2. A list of detected OCR regions on the screen.
        
        Your task is to create a sequence of drawing actions that synchronize with the teacher's speech.
        
        Transcript Segments:
        {json.dumps(transcript_data, indent=2)}
        
        Available OCR Regions:
        {json.dumps(ocr_data, indent=2)}
        
        Rules:
        - Output ONLY a JSON array of actions. No markdown formatting, no explanation.
        - Each action should be a JSON object with:
          - "action_type": string (one of "highlight", "underline", "box")
          - "start_time": float (seconds, match with transcript start time)
          - "end_time": float (seconds, match with transcript end time)
          - "target_box": object {{"x_min": int, "y_min": int, "x_max": int, "y_max": int}} (Select an appropriate region box based on context)
          - "color": string (e.g., "red", "blue", "green", "yellow")
          - "thickness": int (e.g., 2, 4)
        
        Create a logical sequence of highlights or underlines as the teacher speaks.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up response if it contains markdown code blocks
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
                
            actions_data = json.loads(result_text.strip())
            
            actions = []
            for item in actions_data:
                box_data = item.get("target_box", {})
                
                action = AnnotationAction(
                    action_type=item.get("action_type", "highlight"),
                    start_time=float(item.get("start_time", 0.0)),
                    end_time=float(item.get("end_time", 1.0)),
                    color=item.get("color", "red"),
                    thickness=int(item.get("thickness", 2))
                )
                
                # Check if box_data is not empty
                if box_data and all(k in box_data for k in ("x_min", "y_min", "x_max", "y_max")):
                    from ..models.core import BoundingBox
                    action.target_box = BoundingBox(
                        x_min=box_data["x_min"],
                        y_min=box_data["y_min"],
                        x_max=box_data["x_max"],
                        y_max=box_data["y_max"]
                    )
                
                actions.append(action)
                
            # Determine total duration
            duration = transcript.segments[-1].end if transcript.segments else 0.0
            
            timeline = Timeline(actions=actions, duration=duration)
            log.info(f"Generated timeline with {len(actions)} actions.")
            return timeline
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse LLM JSON output: {e}\nResponse: {response.text}")
            raise LLMProcessingError("LLM returned invalid JSON.")
        except Exception as e:
            log.error(f"LLM request failed: {e}")
            raise LLMProcessingError(f"Failed to generate timeline: {e}")
