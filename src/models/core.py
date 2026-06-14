from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple

class TranscriptWord(BaseModel):
    """A single transcribed word with timing."""
    word: str
    start: float
    end: float
    probability: float

class TranscriptSegment(BaseModel):
    """A segment of transcribed text (usually a sentence or phrase)."""
    id: int
    text: str
    start: float
    end: float
    words: List[TranscriptWord] = Field(default_factory=list)

class Transcript(BaseModel):
    """The full transcript of an audio file."""
    text: str
    segments: List[TranscriptSegment]

class BoundingBox(BaseModel):
    """A bounding box for an OCR element [x_min, y_min, x_max, y_max]."""
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    
    @property
    def center(self) -> Tuple[int, int]:
        return ((self.x_min + self.x_max) // 2, (self.y_min + self.y_max) // 2)
    
    @property
    def width(self) -> int:
        return self.x_max - self.x_min
        
    @property
    def height(self) -> int:
        return self.y_max - self.y_min

class OCRElement(BaseModel):
    """Detected text or equation element from OCR."""
    id: str
    text: str
    box: BoundingBox
    semantic_type: str = "general_text" # 'math_formula', 'diagram', 'mcq_option', 'general_text'
    confidence: float = 1.0

class OCRResult(BaseModel):
    """Full OCR result for an image."""
    elements: List[OCRElement]
    image_width: int
    image_height: int
    avg_confidence: float = 1.0

class AnnotationAction(BaseModel):
    """An action to be drawn on the video."""
    action_type: str  # highlight, underline, circle, rectangle, label, arrow, curved_arrow, write_formula, handwriting, eraser
    start_time: float
    end_time: float
    target_box: Optional[BoundingBox] = None
    source_box: Optional[BoundingBox] = None # Used for arrows (from source to target)
    color: str = "red"
    thickness: int = 2
    # For 'draw_path' or 'handwriting'
    path_points: Optional[List[Tuple[int, int]]] = None
    # For 'write_text' or 'write_formula' or 'label'
    text: Optional[str] = None
    text_position: Optional[Tuple[int, int]] = None
    confidence: float = 1.0

class Timeline(BaseModel):
    """A collection of annotation actions synchronized with audio."""
    actions: List[AnnotationAction]
    duration: float
    avg_confidence: float = 1.0

class ExplanationSummary(BaseModel):
    key_concepts: List[str]
    formula_used: List[str]
    final_answer: Optional[str] = None
    difficulty_level: str

class TeacherAnalytics(BaseModel):
    wpm: float
    total_pause_duration: float
    annotation_density: float
    explanation_quality_score: int
    summary: Optional[ExplanationSummary] = None

class VideoProject(BaseModel):
    """Overall project state."""
    project_id: str
    image_path: str
    audio_path: str
    language: str = "en"
    transcript: Optional[Transcript] = None
    ocr_result: Optional[OCRResult] = None
    timeline: Optional[Timeline] = None
    analytics: Optional[TeacherAnalytics] = None
    output_video_path: Optional[str] = None
