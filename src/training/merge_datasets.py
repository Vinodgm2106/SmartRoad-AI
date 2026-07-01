from pathlib import Path
import shutil

MERGED = Path("data/merged")

for split in ["train", "valid", "test"]:
    (MERGED / split / "images").mkdir(parents=True, exist_ok=True)
    (MERGED / split / "labels").mkdir(parents=True, exist_ok=True)

datasets = [
    Path("data/raw/dataset_1_pothole"),
    Path("data/dataset_2_yolo")
]

for dataset in datasets:
    for split in ["train", "valid", "test"]:

        img_src = dataset / split / "images"
        lbl_src = dataset / split / "labels"

        for img in img_src.glob("*"):
            new_name = f"{dataset.name}_{img.name}"

            shutil.copy(
                img,
                MERGED / split / "images" / new_name
            )

        for lbl in lbl_src.glob("*.txt"):
            new_name = f"{dataset.name}_{lbl.name}"

            shutil.copy(
                lbl,
                MERGED / split / "labels" / new_name
            )

print("Merge completed successfully.")