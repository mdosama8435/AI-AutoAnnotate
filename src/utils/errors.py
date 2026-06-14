class ExplainInkError(Exception):
    """Base exception for all ExplainInk errors."""
    pass

class AudioProcessingError(ExplainInkError):
    """Raised when audio transcription or processing fails."""
    pass

class OCRProcessingError(ExplainInkError):
    """Raised when OCR or image processing fails."""
    pass

class LLMProcessingError(ExplainInkError):
    """Raised when LLM communication or parsing fails."""
    pass

class VideoGenerationError(ExplainInkError):
    """Raised when video rendering or assembly fails."""
    pass

class CapabilityError(ExplainInkError):
    """Raised when a required system capability is missing."""
    pass
