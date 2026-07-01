from ultralytics import YOLO

model = YOLO(
    "models/best.pt"
)

import os
from pathlib import Path

# Resolve test source paths
test_dir = Path("data/merged/test/images")
label_dir = Path("data/merged/test/labels")
source = ""

if test_dir.exists():
    found_with_detections = False
    if label_dir.exists():
        for label_file in label_dir.glob("*.txt"):
            if label_file.stat().st_size > 0: # has label details
                img_path = test_dir / f"{label_file.stem}.jpg"
                if img_path.exists():
                    source = str(img_path)
                    found_with_detections = True
                    print(f"📂 Found test image with annotated defects: {source}\n")
                    break
    
    if not found_with_detections:
        test_images = sorted(list(test_dir.glob("*.jpg")))
        if test_images:
            source = str(test_images[0])
            print(f"📂 Found test dataset. Running prediction on: {source}\n")
        else:
            source = str(test_dir)
            print(f"📂 Running prediction on directory: {source}\n")
else:
    print("❌ Error: Could not find 'data/merged/test/images'. Please make sure the dataset is placed correctly.")
    exit(1)

results = model.predict(
    source=source,
    conf=0.25,
    save=True,
    project=str(Path("runs/detect").resolve()),
    name="predict"
)

for r in results:
    print("\nDetected Objects:")
    if len(r.boxes) == 0:
        print("  None detected (Road surface looks clean!)")
    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        print(f"  🎯 {model.names[cls_id]} ({conf:.2f})")

print(f"\n🎉 Prediction Complete! Annotated output saved to: runs/detect/")