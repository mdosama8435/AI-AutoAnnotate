import os
from faster_whisper import WhisperModel
from ..models.core import Transcript, TranscriptSegment, TranscriptWord
from ..utils.logger import log
from ..utils.errors import AudioProcessingError
from ..utils.capabilities import check_gpu

class AudioTranscriber:
    """Handles audio transcription using faster-whisper."""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.device = "cuda" if check_gpu() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        log.info(f"Initializing WhisperModel ({self.model_size}) on {self.device} with {self.compute_type}")
        try:
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type
            )
            log.info("WhisperModel initialized successfully.")
        except Exception as e:
            log.error(f"Failed to initialize WhisperModel: {e}")
            raise AudioProcessingError(f"Could not load faster-whisper model: {e}")

    def transcribe(self, audio_path: str, language: str = "auto") -> Transcript:
        """Transcribe an audio file and return a Transcript object with word-level timestamps."""
        if not os.path.exists(audio_path):
            raise AudioProcessingError(f"Audio file not found: {audio_path}")
            
        log.info(f"Starting transcription for {audio_path} (Language: {language})")
        
        # Prepare kwargs
        transcribe_kwargs = {"beam_size": 5, "word_timestamps": True}
        if language != "auto":
            transcribe_kwargs["language"] = language
        try:
            segments_gen, info = self.model.transcribe(
                audio_path,
                **transcribe_kwargs
            )
            
            log.info(f"Detected language '{info.language}' with probability {info.language_probability}")
            
            transcript_segments = []
            full_text = ""
            total_prob = 0.0
            word_count = 0
            
            for segment in segments_gen:
                words = []
                if segment.words:
                    for w in segment.words:
                        words.append(
                            TranscriptWord(
                                word=w.word,
                                start=w.start,
                                end=w.end,
                                probability=w.probability
                            )
                        )
                        total_prob += w.probability
                        word_count += 1
                
                t_seg = TranscriptSegment(
                    id=segment.id,
                    text=segment.text,
                    start=segment.start,
                    end=segment.end,
                    words=words
                )
                transcript_segments.append(t_seg)
                full_text += segment.text + " "
                
            avg_confidence = total_prob / word_count if word_count > 0 else 1.0
            log.info(f"Transcription completed successfully. Avg Confidence: {avg_confidence:.2f}")
            
            # Since Transcript doesn't have avg_confidence right now (we didn't add it to Transcript, but maybe we should)
            # Let's just return it or log it. Wait, I didn't add confidence to Transcript model, just the word level.
            # We can still calculate it and perhaps we should add it. I'll add it to Transcript in core.py later or just leave it.
            # For now just return the Transcript.
            
            return Transcript(text=full_text.strip(), segments=transcript_segments)
            
        except Exception as e:
            log.error(f"Transcription failed: {e}")
            raise AudioProcessingError(f"Transcription process failed: {e}")
