import json
import google.generativeai as genai
from ..models.core import VideoProject, TeacherAnalytics, ExplanationSummary
from ..utils.config import settings
from ..utils.logger import log

class AnalyticsEngine:
    """Generates pedagogical insights and teacher analytics from a project."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            
    def generate_analytics(self, project: VideoProject) -> TeacherAnalytics:
        log.info(f"Generating analytics for {project.project_id}")
        
        # 1. Calculate WPM
        total_words = 0
        total_duration = 0.0
        total_pause = 0.0
        
        if project.transcript and project.transcript.segments:
            for i, seg in enumerate(project.transcript.segments):
                total_words += len(seg.words) if seg.words else len(seg.text.split())
                
                if i > 0:
                    prev_seg = project.transcript.segments[i-1]
                    gap = seg.start - prev_seg.end
                    if gap > 1.0: # Only count pauses longer than 1 second
                        total_pause += gap
            
            total_duration = project.transcript.segments[-1].end
        
        wpm = (total_words / total_duration) * 60 if total_duration > 0 else 0
        
        # 2. Calculate Annotation Density (actions per minute)
        density = 0.0
        if project.timeline and project.timeline.actions and total_duration > 0:
            action_count = len(project.timeline.actions)
            density = (action_count / total_duration) * 60
            
        # 3. Generate Summary & Quality Score using LLM
        summary = None
        quality_score = 75 # Default fallback
        
        if self.api_key and project.transcript and project.ocr_result:
            transcript_text = project.transcript.text
            ocr_texts = [e.text for e in project.ocr_result.elements]
            
            prompt = f"""
            You are an expert pedagogical evaluator. Analyze the following educational transcript and on-screen text.
            
            Transcript: {transcript_text}
            On-Screen Text: {ocr_texts}
            
            Evaluate the explanation. Return ONLY a JSON object with this exact structure:
            {{
                "key_concepts": ["concept 1", "concept 2"],
                "formula_used": ["formula 1"],
                "final_answer": "the answer if applicable, else null",
                "difficulty_level": "Beginner | Intermediate | Advanced",
                "explanation_quality_score": <integer 1-100>
            }}
            """
            
            try:
                response = self.model.generate_content(prompt)
                result_text = response.text.strip()
                if result_text.startswith("```json"): result_text = result_text[7:]
                if result_text.startswith("```"): result_text = result_text[3:]
                if result_text.endswith("```"): result_text = result_text[:-3]
                
                data = json.loads(result_text.strip())
                summary = ExplanationSummary(
                    key_concepts=data.get("key_concepts", []),
                    formula_used=data.get("formula_used", []),
                    final_answer=data.get("final_answer"),
                    difficulty_level=data.get("difficulty_level", "Beginner")
                )
                quality_score = int(data.get("explanation_quality_score", 75))
            except Exception as e:
                log.error(f"Failed to generate AI Summary: {e}")
                
        analytics = TeacherAnalytics(
            wpm=round(wpm, 1),
            total_pause_duration=round(total_pause, 1),
            annotation_density=round(density, 1),
            explanation_quality_score=quality_score,
            summary=summary
        )
        
        project.analytics = analytics
        return analytics
