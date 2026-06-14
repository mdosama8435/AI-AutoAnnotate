import time
import json
import os
from ..storage.manager import StorageManager
from ..audio.transcriber import AudioTranscriber
from ..ocr.detector import OCRDetector
from ..ocr.semantic import SemanticDetector
from ..llm.engines import NextGenPlanner, RuleBasedPlanner
from ..video.assembler import VideoAssembler
from ..models.core import VideoProject
from ..utils.logger import log

class PipelineOrchestrator:
    """Master service that coordinates the advanced video generation process."""
    
    def __init__(self):
        log.info("Initializing Pipeline Orchestrator with Next-Gen Engines...")
        self.storage = StorageManager()
        self.audio = AudioTranscriber()
        self.ocr = OCRDetector()
        self.semantic_ocr = SemanticDetector()
        
        from ..utils.config import settings
        if settings.gemini_api_key:
            self.planner = NextGenPlanner()
        else:
            self.planner = RuleBasedPlanner()
            
        self.video = VideoAssembler()
        
    def process(self, project: VideoProject) -> VideoProject:
        """Run the end-to-end processing pipeline."""
        start_time = time.time()
        log.info(f"Starting pipeline for project {project.project_id}")
        
        try:
            # 1. OCR Analysis (Structure)
            log.info("Step 1a: Structural OCR Analysis")
            base_ocr = self.ocr.extract_elements(project.image_path)
            
            # 1b. Semantic Classification
            log.info("Step 1b: Semantic Element Classification")
            project.ocr_result = self.semantic_ocr.classify_elements(project.image_path, base_ocr)
            
            # 2. Audio Transcription
            log.info("Step 2: Audio Transcription")
            project.transcript = self.audio.transcribe(project.audio_path, language=project.language)
            
            # 3. LLM Timeline Planning (Next-Gen)
            log.info("Step 3: Intent & Context Timeline Planning")
            project.timeline = self.planner.generate_timeline(project.transcript, project.ocr_result)
            
            # Save annotation_plan.json
            if project.timeline:
                plan_path = self.storage.get_project_dir(project.project_id) / "annotation_plan.json"
                with open(plan_path, "w") as f:
                    actions_dict = [a.model_dump() for a in project.timeline.actions]
                    json.dump(actions_dict, f, indent=2)
                log.info(f"Saved annotation plan to {plan_path}")
            
            # 4. Video Assembly
            log.info("Step 4: Advanced Video Assembly")
            output_path = self.storage.get_output_path(project.project_id)
            project.output_video_path = self.video.assemble(
                project.image_path,
                project.audio_path,
                project.timeline,
                output_path
            )
            
            elapsed = time.time() - start_time
            log.info(f"Pipeline completed successfully in {elapsed:.2f} seconds.")
            
            return project
            
        except Exception as e:
            log.error(f"Pipeline failed for project {project.project_id}: {e}")
            raise
