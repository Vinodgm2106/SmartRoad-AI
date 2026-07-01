import json
from pathlib import Path

classes = set()

ann_folder = Path(
    "data/raw/dataset_2_road_damage/ds0/ann"
)

for file in ann_folder.glob("*.json"):

    with open(file, "r", encoding="utf-8") as f:

        data = json.load(f)

        for obj in data.get("objects", []):

            classes.add(
                obj["classTitle"]
            )

print()

print("Classes Found:")

for c in sorted(classes):
    print(c)