import os
import shutil
import torch
from ultralytics import YOLO

# Ensure working directory is the project root (so relative paths resolve correctly)
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(script_dir) == "training" and os.path.basename(os.path.dirname(script_dir)) == "src":
    project_root = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(project_root)
    print(f"📁 Working directory automatically set to project root: {os.getcwd()}")

# 1. Detect if GPU (CUDA) is available, otherwise use CPU
device = 0 if torch.cuda.is_available() else "cpu"
print(f"\n🚀 Device Auto-Detection: {'GPU (CUDA)' if device == 0 else 'CPU'}\n")

# Helper to save checkpoints in multiple locations/formats to satisfy requirements
def save_checkpoint(src_path, target_names, target_dirs):
    if not os.path.exists(src_path):
        print(f"⚠️ Warning: Source checkpoint not found at {src_path}")
        return

    for target_dir in target_dirs:
        os.makedirs(target_dir, exist_ok=True)
        for name in target_names:
            dest_path = os.path.join(target_dir, name)
            try:
                shutil.copy(src_path, dest_path)
                print(f"💾 Saved checkpoint to: {dest_path}")
            except Exception as e:
                print(f"❌ Error saving to {dest_path}: {e}")

# Define directories
weights_dir = "runs/train/smartroad_model/weights"
models_dir = "models"
root_dir = "."

# Common training configurations
train_args = {
    "data": "data/merged/data.yaml",
    "epochs": 50,                       # Each phase runs for 50 epochs
    "imgsz": 640,                       # Standard training dimensions
    "batch": 16 if device == 0 else 4,  # Safe batch size: 16 for GPU, 4 for CPU
    "workers": 4 if device == 0 else 0, # Multi-threading: 4 for GPU, disabled for CPU
    "device": device,                   # Run on detected device
    "project": "runs/train"
}

# --- PHASE 1: Epochs 1 to 50 ---
print("\n--- PHASE 1: Training Epochs 1 to 50 ---")
model = YOLO("yolov8n.pt")
model.train(name="smartroad_model_50", **train_args)

# Save Phase 1 weights (Epoch 50) as last.pt and last.py
phase1_src = "runs/train/smartroad_model_50/weights/last.pt"
save_checkpoint(
    src_path=phase1_src,
    target_names=["last.pt", "last.py"],
    target_dirs=[weights_dir, root_dir]
)

# --- PHASE 2: Epochs 51 to 100 ---
print("\n--- PHASE 2: Training Epochs 51 to 100 ---")
# Load the weights from Phase 1
phase2_model_path = os.path.join(weights_dir, "last.pt")
model = YOLO(phase2_model_path)
model.train(name="smartroad_model_100", **train_args)

# Save Phase 2 weights (Epoch 100, consists of 1-100 epochs) as last.pt and last.py
phase2_src = "runs/train/smartroad_model_100/weights/last.pt"
save_checkpoint(
    src_path=phase2_src,
    target_names=["last.pt", "last.py"],
    target_dirs=[weights_dir, root_dir]
)

# --- PHASE 3: Epochs 101 to 150 ---
print("\n--- PHASE 3: Training Epochs 101 to 150 ---")
# Load the weights from Phase 2
phase3_model_path = os.path.join(weights_dir, "last.pt")
model = YOLO(phase3_model_path)
model.train(name="smartroad_model_150", **train_args)

# Save Phase 3 final weights (Epoch 150) as best.pt and models/best.pt
phase3_src_best = "runs/train/smartroad_model_150/weights/best.pt"
phase3_src_last = "runs/train/smartroad_model_150/weights/last.pt"

# Prefer best.pt if generated, fallback to last.pt
final_src = phase3_src_best if os.path.exists(phase3_src_best) else phase3_src_last

save_checkpoint(
    src_path=final_src,
    target_names=["best.pt", "best.py"],
    target_dirs=[weights_dir, models_dir, root_dir]
)

print("\n🎉 150 Epochs Training Pipeline Completed Successfully!")
print("--------------------------------------------------")
print(f"👉 Final best weights are stored at: {os.path.join(models_dir, 'best.pt')}")
print("--------------------------------------------------")