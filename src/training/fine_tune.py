import os
import shutil
import torch
from ultralytics import YOLO

# Ensure working directory is the project root
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(script_dir) == "training" and os.path.basename(os.path.dirname(script_dir)) == "src":
    project_root = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(project_root)
    print(f"📁 Working directory automatically set to project root: {os.getcwd()}")

# 1. Detect if GPU (CUDA) is available, otherwise use CPU
device = 0 if torch.cuda.is_available() else "cpu"
print(f"\n🚀 Device Auto-Detection: {'GPU (CUDA)' if device == 0 else 'CPU'}\n")

# Load current best weights
model_path = "models/best.pt"
if not os.path.exists(model_path):
    print(f"❌ Error: Could not find base weights at {model_path} to fine-tune. Please verify files.")
    exit(1)

print(f"🔄 Loading base model weights from {model_path} for fine-tuning...")
model = YOLO(model_path)

# Fine-tuning configurations with aggressive data augmentations
# to help generalize to varying perspectives, close-ups, and orientations
tune_args = {
    "data": "data/merged/data.yaml",
    "epochs": 50,                       # Fine-tune for 50 epochs
    "imgsz": 640,                       # Training image dimensions
    "batch": 16 if device == 0 else 4,  # Safe batch size: 16 for GPU, 4 for CPU
    "workers": 4 if device == 0 else 0, # Thread workers
    "device": device,                   # Selected device
    "project": "runs/train",
    "name": "smartroad_finetuned",      # Run folder name
    
    # --- Data Augmentations ---
    "degrees": 15.0,                    # Random rotation degrees
    "scale": 0.6,                       # Random scaling (zooms in/out to handle varied camera distances)
    "perspective": 0.0005,              # Random perspective distortions (simulates height/angle changes)
    "flipud": 0.5,                      # Vertical flip probability
    "fliplr": 0.5,                      # Horizontal flip probability
    "mosaic": 1.0,                      # Mix multiple images into a mosaic (great for small/clustered potholes)
    "mixup": 0.15                       # Mixup images (blends images to make background textures less sensitive)
}

print("\n🔥 Starting fine-tuning run with custom data augmentations...")
model.train(**tune_args)

# Copy the new best weights to models/best.pt
new_best = "runs/train/smartroad_finetuned/weights/best.pt"
new_last = "runs/train/smartroad_finetuned/weights/last.pt"
final_dest = "models/best.pt"

src_path = new_best if os.path.exists(new_best) else new_last

if os.path.exists(src_path):
    try:
        shutil.copy(src_path, final_dest)
        print(f"\n✅ Fine-tuning completed! New best weights copied to: {final_dest}")
    except Exception as e:
        print(f"❌ Error copying fine-tuned weights: {e}")
else:
    print(f"❌ Error: Fine-tuned weights not found at {src_path}")
