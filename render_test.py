import os
import time
import moviepy
import logging
from src.video.assembler import VideoAssembler
from src.pipeline.orchestrator import PipelineOrchestrator
from src.models.core import VideoProject

logging.basicConfig(level=logging.INFO)

def run():
    print("="*50)
    print(f"MoviePy Version: {getattr(moviepy, '__version__', 'unknown')}")
    
    # Check ffmpeg availability
    import imageio_ffmpeg
    try:
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"FFmpeg Availability: {ffmpeg_bin}")
    except:
        print("FFmpeg Availability: Defaulting to system 'ffmpeg'")
    print("="*50)
    
    os.makedirs("output", exist_ok=True)
    
    # Find newest project dir
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        print("No temp dir found.")
        return
        
    projects = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
    if not projects:
        print("No project dirs found.")
        return
        
    latest_project = max(projects, key=os.path.getmtime)
    
    image_path = os.path.join(latest_project, "base_image.png")
    # check for mpeg, mp3, wav
    audio_path = None
    for ext in ["mpeg", "mp3", "wav", "m4a"]:
        p = os.path.join(latest_project, f"narration.{ext}")
        if os.path.exists(p):
            audio_path = p
            break
            
    if not os.path.exists(image_path) or not audio_path:
        print("Image or audio not found.")
        return
        
    print(f"Using Image: {image_path}")
    print(f"Using Audio: {audio_path}")
    
    project = VideoProject(
        project_id=os.path.basename(latest_project),
        image_path=image_path,
        audio_path=audio_path
    )
    
    orchestrator = PipelineOrchestrator()
    print("Starting Pipeline (Audio -> OCR -> LLM -> Video)...")
    
    start_time = time.time()
    result = orchestrator.process(project)
    
    # Force output path as requested
    output_path = "output/final_video.mp4"
    orchestrator.video.assemble(image_path, audio_path, result.timeline, output_path)
    
    render_duration = time.time() - start_time
    print("="*50)
    print(f"Render Duration: {render_duration:.2f} seconds")
    print(f"Output File Path: {os.path.abspath(output_path)}")
    print("="*50)

if __name__ == "__main__":
    run()
