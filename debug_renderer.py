import json
import os
import cv2
import sys

# Find newest project dir
temp_dir = "temp"
projects = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
projects_with_plan = [p for p in projects if os.path.exists(os.path.join(p, "annotation_plan.json"))]
latest_project = max(projects_with_plan, key=os.path.getmtime)

print(f"Using project: {latest_project}")
plan_path = os.path.join(latest_project, "annotation_plan.json")
img_path = os.path.join(latest_project, "base_image.png")

if not os.path.exists(plan_path):
    print("Plan not found!")
    sys.exit(1)

with open(plan_path, "r") as f:
    plan_data = json.load(f)

print(f"Total events generated: {len(plan_data)}")
write_events = 0
formula_events = 0
circle_events = 0
underline_events = 0

print("-" * 40)
for a in plan_data:
    at = a.get("action_type")
    print(f"timestamp: {a.get('start_time')} -> {a.get('end_time')} | action: {at} | text: {a.get('text')} | duration: {a.get('end_time') - a.get('start_time')}")
    if at == "write_text": write_events += 1
    elif at == "draw_formula": formula_events += 1
    elif at == "circle": circle_events += 1
    elif at == "underline": underline_events += 1

print("-" * 40)
print(f"Write events: {write_events}")
print(f"Formula events: {formula_events}")
print(f"Circle events: {circle_events}")
print(f"Underline events: {underline_events}")

print("-" * 40)
print("Testing painter.py for time t=70.0 (all events should be visible)...")

from src.renderer.painter import FrameRenderer
from src.models.core import Timeline, AnnotationAction

actions = [AnnotationAction(**a) for a in plan_data]
timeline = Timeline(actions=actions, duration=70.0)
renderer = FrameRenderer()

try:
    frame = renderer.render(img_path, timeline.actions, 70.0)
    print(f"Render successful. Frame shape: {frame.shape}, Max pixel value: {frame.max()}")
    cv2.imwrite("debug_frame.png", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    print("Saved debug_frame.png")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Rendering failed: {e}")

print("-" * 40)
print("Testing painter.py for time t=70.0 (all events should be visible)...")

from src.renderer.painter import FrameRenderer
from src.models.core import Timeline, AnnotationAction

actions = [AnnotationAction(**a) for a in plan_data]
timeline = Timeline(actions=actions, duration=70.0)
renderer = FrameRenderer()

try:
    frame = renderer.render(img_path, timeline.actions, 70.0)
    print(f"Render successful. Frame shape: {frame.shape}, Max pixel value: {frame.max()}")
    cv2.imwrite("debug_frame.png", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    print("Saved debug_frame.png")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Rendering failed: {e}")
