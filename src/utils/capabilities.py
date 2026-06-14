import shutil
import subprocess
from .logger import log
from .errors import CapabilityError

def check_ffmpeg():
    """Check if ffmpeg is installed and available in the system path."""
    if shutil.which("ffmpeg") is None:
        log.error("FFmpeg not found in system path.")
        raise CapabilityError("FFmpeg is required but was not found. Please install FFmpeg and add it to your PATH.")
    try:
        # Just check the version to ensure it actually runs
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        log.info(f"FFmpeg detected: {result.stdout.splitlines()[0]}")
    except Exception as e:
        log.error(f"FFmpeg check failed: {e}")
        raise CapabilityError(f"FFmpeg is installed but failed to execute: {e}")

def check_gpu():
    """Check if a CUDA GPU is available for faster-whisper and other models."""
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            log.info(f"GPU detected: {device_name}")
            return True
        else:
            log.info("No CUDA GPU detected. Falling back to CPU.")
            return False
    except ImportError:
        log.info("PyTorch not installed or accessible. Cannot check for GPU. Assuming CPU.")
        return False
