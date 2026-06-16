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
        transcript_data = []
        for s in transcript.segments:
            transcript_data.append({
                "text": s.text,
                "start": s.start,
                "end": s.end,
                "words": [{"word": w.word, "start": w.start, "end": w.end} for w in s.words]
            })
            
        prompt = f"""
        You are an expert educational video director generating a handwritten math solution video.
        
        Transcript Segments (with exact word-level timestamps):
        {json.dumps(transcript_data, indent=2)}
        
        Your task is to create a sequence of drawing actions that synchronize perfectly with the teacher's speech.
        
        Rules:
        - Output ONLY a JSON array of actions. No markdown formatting, no explanation.
        - Each action should be a JSON object with:
          - "action_type": string (MUST be "write_formula", "handwriting", or "answer_box")
          - "spoken_phrase": string (the exact phrase spoken that triggers this step)
          - "start_time": float (exact start time of the first word in the phrase, from the provided word timestamps)
          - "end_time": float (exact end time of the last word in the phrase)
          - "text": string (the exact math formula or text to render)
        
        Guidelines:
        - DO NOT use pink overlays, highlights, rectangles, or opaque boxes.
        - Render handwritten annotations only.
        - Write formulas progressively exactly when they are spoken. 
        - E.g. When narration says "distance formula", text should be "d = \\sqrt{{(x_2 - x_1)^2 + (y_2 - y_1)^2}}".
        - Render each step only when narration reaches that step.
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
                action = AnnotationAction(
                    action_type=item.get("action_type", "write_formula"),
                    spoken_phrase=item.get("spoken_phrase", ""),
                    start_time=float(item.get("start_time", 0.0)),
                    end_time=float(item.get("end_time", 1.0)),
                    color="dark blue",
                    thickness=2,
                    text=item.get("text", "")
                )
                actions.append(action)
                
            # Determine total duration
            duration = transcript.segments[-1].end if transcript.segments else 0.0
            
            timeline = Timeline(actions=actions, duration=duration)
            log.info(f"Generated timeline with {len(actions)} progressive handwriting actions.")
            return timeline
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse LLM JSON output: {e}\nResponse: {response.text}")
            raise LLMProcessingError("LLM returned invalid JSON.")
        except Exception as e:
            log.error(f"LLM request failed: {e}")
            raise LLMProcessingError(f"Failed to generate timeline: {e}")
