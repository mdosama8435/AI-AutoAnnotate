import os
import shutil
from pathlib import Path
import uuid
from ..utils.config import settings
from ..utils.logger import log

class StorageManager:
    """Manages files and directories for video projects."""
    
    def __init__(self):
        self.temp_dir = settings.temp_dir
        self.output_dir = settings.output_dir
    
    def create_project(self) -> str:
        """Create a new project directory and return the project ID."""
        project_id = str(uuid.uuid4())
        project_dir = self.temp_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Created project directory for {project_id}")
        return project_id
    
    def save_upload(self, project_id: str, filename: str, content: bytes) -> str:
        """Save an uploaded file to the project directory."""
        project_dir = self.temp_dir / project_id
        if not project_dir.exists():
            project_dir.mkdir(parents=True, exist_ok=True)
            
        file_path = project_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        log.info(f"Saved uploaded file {filename} to {project_id}")
        return str(file_path)
        
    def get_project_dir(self, project_id: str) -> Path:
        """Get the directory path for a project."""
        return self.temp_dir / project_id
        
    def get_output_path(self, project_id: str, filename: str = "output.mp4") -> str:
        """Get the path for the final output video."""
        project_out = self.output_dir / project_id
        project_out.mkdir(parents=True, exist_ok=True)
        return str(project_out / filename)
        
    def cleanup_project(self, project_id: str):
        """Remove temporary files for a project."""
        project_dir = self.temp_dir / project_id
        if project_dir.exists():
            shutil.rmtree(project_dir)
            log.info(f"Cleaned up project directory for {project_id}")
