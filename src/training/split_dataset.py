from pathlib import Path
import random
import shutil

random.seed(42)

base = Path("F:/SmartRoad-AI/data/raw")

train_images = list((base / "train/images").glob("*.*"))

random.shuffle(train_images)

total = len(train_images)

valid_size = int(total * 0.1)
test_size = int(total * 0.1)

valid_imgs = train_images[:valid_size]
test_imgs = train_images[valid_size:valid_size+test_size]

for img_path in valid_imgs:

    label_path = (
        base / "train/labels" /
        (img_path.stem + ".txt")
    )

    shutil.move(
        str(img_path),
        str(base / "valid/images" / img_path.name)
    )

    shutil.move(
        str(label_path),
        str(base / "valid/labels" / label_path.name)
    )

for img_path in test_imgs:

    label_path = (
        base / "train/labels" /
        (img_path.stem + ".txt")
    )

    shutil.move(
        str(img_path),
        str(base / "test/images" / img_path.name)
    )

    shutil.move(
        str(label_path),
        str(base / "test/labels" / label_path.name)
    )

print("Dataset split completed.")