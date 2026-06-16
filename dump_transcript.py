import os
from src.audio.transcriber import AudioTranscriber

temp_dir = "temp"
projects = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
latest_project = max(projects, key=os.path.getmtime)
audio_path = os.path.join(latest_project, "narration.mpeg")

transcriber = AudioTranscriber()
transcript = transcriber.transcribe(audio_path)

print("\n--- TRANSCRIPT ---")
for seg in transcript.segments:
    print(f"[{seg.start:.2f} - {seg.end:.2f}] {seg.text}")
print("------------------\n")
