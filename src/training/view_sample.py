import cv2
import matplotlib.pyplot as plt
from pathlib import Path

img_path = list(
    Path("data/raw/train/images").glob("*")
)[0]

img = cv2.imread(str(img_path))

img = cv2.cvtColor(
    img,
    cv2.COLOR_BGR2RGB
)

plt.imshow(img)
plt.axis("off")
plt.show()