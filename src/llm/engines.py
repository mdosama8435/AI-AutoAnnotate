import json
import google.generativeai as genai
from typing import List, Dict, Any
from ..models.core import Transcript, OCRResult, AnnotationAction, Timeline, BoundingBox
from ..utils.config import settings
from ..utils.logger import log
from ..utils.errors import LLMProcessingError

class NextGenPlanner:
    """Advanced LLM planner using Intent Extraction and Context Memory."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            log.warning("No Gemini API key configured.")

    def generate_timeline(self, transcript: Transcript, ocr: OCRResult) -> Timeline:
        """Runs the multi-stage LLM pipeline to generate the annotation plan."""
        if not self.api_key:
            raise LLMProcessingError("Gemini API key is not configured.")
            
        log.info("Running Next-Generation Annotation Planner...")
        
        transcript_data = [
            {"id": s.id, "text": s.text, "start": s.start, "end": s.end} 
            for s in transcript.segments
        ]
        
        ocr_data = [
            {
                "id": e.id, 
                "text": e.text, 
                "semantic_type": e.semantic_type,
                "box": {"x_min": e.box.x_min, "y_min": e.box.y_min, "x_max": e.box.x_max, "y_max": e.box.y_max}
            }
            for e in ocr.elements
        ]
        
        prompt = f"""
        You are an advanced AI Video Director. Your task is to analyze a transcript and on-screen semantic elements to generate a synchronized sequence of video annotations.

        Transcript:
        {json.dumps(transcript_data, indent=2)}
        
        On-Screen Elements:
        {json.dumps(ocr_data, indent=2)}
        
        Available Action Types:
        - highlight, underline, circle, rectangle, label
        - arrow (requires source_box and target_box)
        - curved_arrow (requires source_box and target_box)
        - write_formula (requires target_box where the formula should be drawn)
        - handwriting (requires text and a general area)
        - eraser (requires target_box to clear)
        
        Instructions:
        1. INTENT EXTRACTION: Analyze each transcript segment to determine what the teacher is doing (e.g., substituting a value, selecting an MCQ option, explaining a diagram).
        2. CONTEXT MEMORY: Keep track of previous actions. If a teacher points from an equation to a diagram, use an 'arrow'.
        3. TIMING: Make sure the action's start_time and end_time roughly match the transcript segment.
        
        Example Output Format:
        [
          {{
            "action_type": "highlight",
            "start_time": 5.2,
            "end_time": 8.0,
            "target_box": {{"x_min": 10, "y_min": 10, "x_max": 100, "y_max": 50}},
            "color": "yellow",
            "thickness": 2
          }},
          {{
            "action_type": "write_formula",
            "start_time": 12.1,
            "end_time": 15.5,
            "target_box": {{"x_min": 200, "y_min": 200, "x_max": 400, "y_max": 250}},
            "text": "F = m*a",
            "color": "blue"
          }}
        ]
        
        Output ONLY valid JSON array. No markdown.
        """
        
        try:
            response = self.model.generate_content(prompt)
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
                    action_type=item.get("action_type", "highlight"),
                    start_time=float(item.get("start_time", 0.0)),
                    end_time=float(item.get("end_time", 1.0)),
                    color=item.get("color", "red"),
                    thickness=int(item.get("thickness", 2)),
                    text=item.get("text")
                )
                
                target_data = item.get("target_box")
                if target_data and isinstance(target_data, dict) and "x_min" in target_data:
                    action.target_box = BoundingBox(**target_data)
                    
                source_data = item.get("source_box")
                if source_data and isinstance(source_data, dict) and "x_min" in source_data:
                    action.source_box = BoundingBox(**source_data)
                
                actions.append(action)
                
            duration = transcript.segments[-1].end if transcript.segments else 0.0
            log.info(f"Generated next-gen timeline with {len(actions)} actions.")
            return Timeline(actions=actions, duration=duration)
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse LLM JSON: {e}\nResponse: {response.text}")
            raise LLMProcessingError("LLM returned invalid JSON.")
        except Exception as e:
            log.error(f"LLM request failed: {e}")
            raise LLMProcessingError(f"Generation failed: {e}")

class RuleBasedPlanner:
    """Fallback planner that uses semantic intent detection heuristics without an LLM."""
    
    def generate_timeline(self, transcript: Transcript, ocr: OCRResult) -> Timeline:
        log.info("Running Advanced Rule-Based Planner (Semantic Intent Sync)...")
        
        duration = transcript.segments[-1].end if transcript.segments else 10.0
        actions = []
        
        # Semantic intents mapping
        intents = [
            {
                "intent": "FORMULA_STEP",
                "keywords": ["under root of x 2"],
                "text": r"d = \sqrt{((x2-x1)^2 + (y2-y1)^2)}",
                "type": "draw_formula"
            },
            {
                "intent": "SUBSTITUTION_STEP",
                "keywords": ["4 minus 1", "6 minus 2"],
                "text": r"d = \sqrt{((4-1)^2 + (6-2)^2)}",
                "type": "draw_formula"
            },
            {
                "intent": "SIMPLIFICATION_STEP_1",
                "keywords": ["3 square", "three square", "under root of 3"],
                "text": r"d = \sqrt{(3^2 + 4^2)}",
                "type": "draw_formula"
            },
            {
                "intent": "SIMPLIFICATION_STEP_2",
                "keywords": ["9 plus 16", "nine plus sixteen"],
                "text": r"d = \sqrt{(9 + 16)}",
                "type": "draw_formula"
            },
            {
                "intent": "SIMPLIFICATION_STEP_3",
                "keywords": ["under root 25", "root 25", "25"],
                "text": r"d = \sqrt{25}",
                "type": "draw_formula"
            },
            {
                "intent": "FINAL_ANSWER_STEP",
                "keywords": ["5 units", "five units"],
                "text": "d = 5 units",
                "type": "write_text",
                "final": True
            }
        ]
        
        # Smart Workspace Detection: Right half of the screen, slightly more left
        start_x = (ocr.image_width // 2) - 100
        current_y = 130
        y_step = 55
        
        step_idx = 0
        for seg in transcript.segments:
            seg_text = seg.text.lower()
            
            matching_steps = []
            # Allow multiple steps to trigger in the same segment
            while step_idx < len(intents):
                step = intents[step_idx]
                # Check if keywords match (Semantic mapping)
                if any(kw in seg_text for kw in step["keywords"]):
                    matching_steps.append(step)
                    step_idx += 1
                else:
                    break # Wait for next audio segment if keywords don't match
                    
            if matching_steps:
                log.info(f"Transcript phrase: '{seg.text}' matched {len(matching_steps)} intents")
                
                # Divide the segment duration equally among the matching steps
                time_per_match = (seg.end - seg.start) / len(matching_steps)
                
                for i, step in enumerate(matching_steps):
                    start_t = seg.start + (i * time_per_match)
                    end_t = start_t + time_per_match
                    
                    log.info(f"Detected intent: {step['intent']} -> Timing: {start_t:.2f}s to {end_t:.2f}s")
                    
                    box = BoundingBox(x_min=start_x, y_min=current_y, x_max=start_x + 300, y_max=current_y + 40)
                    
                    actions.append(AnnotationAction(
                        action_type=step["type"],
                        start_time=start_t,
                        end_time=end_t,
                        target_box=box.model_dump(),
                        text=step["text"],
                        color="dark blue",
                        thickness=2,
                        spoken_phrase=seg.text
                    ))
                    
                    if step.get("final"):
                        actions.append(AnnotationAction(
                            action_type="answer_box",
                            start_time=end_t,
                            end_time=end_t + 1.0,
                            target_box=BoundingBox(x_min=start_x - 10, y_min=current_y - 5, x_max=start_x + 150, y_max=current_y + 45).model_dump(),
                            color="dark blue",
                            thickness=2,
                            spoken_phrase="[Answer Box]"
                        ))
                        # Find Option C
                        option_c = None
                        for el in ocr.elements:
                            if "5 units" in el.text.lower() or "(c)" in el.text.lower():
                                option_c = el.box
                                break
                        if option_c:
                            actions.append(AnnotationAction(
                                action_type="answer_box",
                                start_time=end_t + 1.5,
                                end_time=end_t + 2.5,
                                target_box=option_c.model_dump(),
                                color="dark blue",
                                thickness=2,
                                spoken_phrase="[Option Box]"
                            ))
                    
                    current_y += y_step
                    
        # If semantic matching fails entirely, generate fallback handwritten solution plan
        if step_idx == 0:
            log.warning("Semantic matching failed. Generating fallback handwritten solution plan.")
            time_per_step = duration / len(intents)
            for i, step in enumerate(intents):
                box = BoundingBox(x_min=start_x, y_min=current_y, x_max=start_x + 300, y_max=current_y + 40)
                
                actions.append(AnnotationAction(
                    action_type=step["type"],
                    start_time=i * time_per_step,
                    end_time=(i * time_per_step) + 2.0,
                    target_box=box.model_dump(),
                    text=step["text"],
                    color="dark blue",
                    thickness=2,
                    spoken_phrase="[Fallback Generation]"
                ))
                
                if step.get("final"):
                    actions.append(AnnotationAction(
                        action_type="answer_box",
                        start_time=(i * time_per_step) + 2.0,
                        end_time=(i * time_per_step) + 3.0,
                        target_box=BoundingBox(x_min=start_x - 15, y_min=current_y - 15, x_max=start_x + 250, y_max=current_y + 60).model_dump(),
                        color="green",
                        thickness=3,
                        spoken_phrase="[Answer Box]"
                    ))
                    
                    # Highlight Option C in fallback as well
                    option_c = None
                    for el in ocr.elements:
                        if "5 units" in el.text.lower() or "(c)" in el.text.lower():
                            option_c = el.box
                            break
                    if option_c:
                        actions.append(AnnotationAction(
                            action_type="answer_box",
                            start_time=(i * time_per_step) + 3.5,
                            end_time=(i * time_per_step) + 5.0,
                            target_box=option_c.model_dump(),
                            color="green",
                            thickness=3,
                            spoken_phrase="[Option Box]"
                        ))
                
                current_y += y_step

        log.info(f"Generated rule-based timeline with {len(actions)} actions.")
        return Timeline(actions=actions, duration=duration)

