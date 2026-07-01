import json
import shutil
from pathlib import Path

# Class mapping
CLASS_MAP = {
    "pothole": 0,
    "longitudinal crack": 1,
    "lateral crack": 2,
    "alligator crack": 3
}

IMG_DIR = Path("data/raw/dataset_2_road_damage/ds0/img")
ANN_DIR = Path("data/raw/dataset_2_road_damage/ds0/ann")

OUT_IMG_DIR = Path("data/dataset_2_yolo/images")
OUT_LABEL_DIR = Path("data/dataset_2_yolo/labels")

OUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
OUT_LABEL_DIR.mkdir(parents=True, exist_ok=True)

count = 0

for json_file in ANN_DIR.glob("*.json"):

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    width = data["size"]["width"]
    height = data["size"]["height"]

    image_name = json_file.stem.replace(".jpeg", "") + ".jpeg"

    image_path = IMG_DIR / image_name

    if not image_path.exists():
        continue

    label_path = OUT_LABEL_DIR / (image_path.stem + ".txt")

    lines = []

    for obj in data.get("objects", []):

        cls_name = obj["classTitle"]

        if cls_name not in CLASS_MAP:
            continue

        cls_id = CLASS_MAP[cls_name]

        x1, y1 = obj["points"]["exterior"][0]
        x2, y2 = obj["points"]["exterior"][1]

        x_center = ((x1 + x2) / 2) / width
        y_center = ((y1 + y2) / 2) / height

        box_width = abs(x2 - x1) / width
        box_height = abs(y2 - y1) / height

        lines.append(
            f"{cls_id} {x_center} {y_center} {box_width} {box_height}"
        )

    with open(label_path, "w") as f:
        f.write("\n".join(lines))

    shutil.copy(image_path, OUT_IMG_DIR / image_name)

    count += 1

print(f"\nConverted {count} images successfully.")