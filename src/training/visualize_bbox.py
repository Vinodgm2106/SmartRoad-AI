import cv2
import matplotlib.pyplot as plt
from pathlib import Path

img_path = list(
    Path("data/raw/train/images").glob("*")
)[0]

label_path = (
    Path("data/raw/train/labels")
    / (img_path.stem + ".txt")
)
print("Image:", img_path.name)
img = cv2.imread(str(img_path))

h, w, _ = img.shape

with open(label_path, "r") as f:

    for line in f.readlines():

        cls, xc, yc, bw, bh = map(
            float,
            line.strip().split()
        )

        x1 = int((xc - bw/2) * w)
        y1 = int((yc - bh/2) * h)

        x2 = int((xc + bw/2) * w)
        y2 = int((yc + bh/2) * h)

        cv2.rectangle(
            img,
            (x1, y1),
            (x2, y2),
            (0,255,0),
            2
        )

img = cv2.cvtColor(
    img,
    cv2.COLOR_BGR2RGB
)

plt.figure(figsize=(8,6))
plt.imshow(img)
plt.axis("off")
plt.show()