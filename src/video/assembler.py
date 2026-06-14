import moviepy
from moviepy import VideoClip, AudioFileClip, ImageClip, TextClip, CompositeVideoClip
from ..models.core import Timeline, AnnotationAction
from ..renderer.painter import FrameRenderer
from ..utils.logger import log
from ..utils.errors import VideoGenerationError
import numpy as np

class VideoAssembler:
    """Assembles rendered frames and audio into a final MP4 video."""
    
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.renderer = FrameRenderer()
        
    def assemble(self, image_path: str, audio_path: str, timeline: Timeline, output_path: str) -> str:
        """Generate the final video with annotations synced to audio."""
        moviepy_version = getattr(moviepy, '__version__', 'unknown')
        log.info(f"Starting video assembly using MoviePy v{moviepy_version}. Output to {output_path}")
        
        try:
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            duration = min(timeline.duration, audio_clip.duration) if timeline.duration > 0 else audio_clip.duration
            
            # Create a frame generator function for MoviePy
            def make_frame(t):
                # Returns an RGB numpy array for the frame at time t
                return self.renderer.render(image_path, timeline.actions, t)
                
            # Create video clip from function
            video_clip = VideoClip(make_frame, duration=duration)
            
            # Version-safe audio setting
            if hasattr(video_clip, "with_audio"):
                # MoviePy 2.x API
                video_clip = video_clip.with_audio(audio_clip)
            elif hasattr(video_clip, "set_audio"):
                # MoviePy 1.x API
                video_clip = video_clip.set_audio(audio_clip)
            
            # Write to file
            log.info("Writing video file...")
            video_clip.write_videofile(
                output_path, 
                fps=self.fps, 
                codec="libx264", 
                audio_codec="aac",
                logger=None # Suppress moviepy standard output
            )
            
            # Cleanup clips
            video_clip.close()
            audio_clip.close()
            
            log.info(f"Video generated successfully at {output_path}")
            return output_path
            
        except Exception as e:
            log.error(f"Video assembly failed: {e}")
            raise VideoGenerationError(f"Failed to assemble video: {e}")
