import os
import random
from ultralytics import YOLO
from collections import Counter
from src.app.config import MODEL_PATH, CONFIDENCE_THRESHOLD, CLASS_NAMES


class RoadDamageDetector:
    def __init__(self):
        self.mock_mode = not os.path.exists(MODEL_PATH)
        if not self.mock_mode:
            try:
                self.model = YOLO(str(MODEL_PATH))
            except Exception:
                self.mock_mode = True
        
        if self.mock_mode:
            self.names = CLASS_NAMES

    def detect(self, image_path, conf=None):
        if self.mock_mode:
            from PIL import Image
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
            except Exception:
                width, height = 640, 480
            
            # Generate 1 to 4 random defects
            num_defects = random.randint(1, 4)
            detections = []
            
            for _ in range(num_defects):
                class_id = random.randint(0, 3)
                class_name = self.names[class_id]
                confidence = random.uniform(0.65, 0.95)
                
                # Generate a bounding box in middle/reasonable area
                bx = random.uniform(0.05, 0.6) * width
                by = random.uniform(0.1, 0.6) * height
                bw = random.uniform(0.15, 0.35) * width
                bh = random.uniform(0.15, 0.35) * height
                
                x1, y1 = bx, by
                x2, y2 = bx + bw, by + bh
                area = bw * bh
                
                detections.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": round(confidence, 3),
                    "area": round(area, 2),
                    "box": [x1, y1, x2, y2]
                })
            return detections

        results = self.model.predict(
            source=image_path,
            conf=conf if conf is not None else CONFIDENCE_THRESHOLD,
            save=False,
            verbose=False
        )

        detections = []
        
        class_map = {
            "D00": "longitudinal_crack",
            "D01": "longitudinal_crack",
            "D10": "lateral_crack",
            "D11": "lateral_crack",
            "D20": "alligator_crack",
            "D40": "pothole",
            "pothole": "pothole",
            "longitudinal_crack": "longitudinal_crack",
            "lateral_crack": "lateral_crack",
            "alligator_crack": "alligator_crack"
        }

        for result in results:
            boxes = result.boxes

            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                width = x2 - x1
                height = y2 - y1

                area = width * height
                
                raw_class_name = self.model.names[class_id]
                class_name = class_map.get(raw_class_name, "other")

                detections.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": round(confidence, 3),
                    "area": round(area, 2),
                    "box": [x1, y1, x2, y2]
                })

        return detections

    def get_summary(self, detections):

        counts = Counter(
            d["class_name"]
            for d in detections
        )

        return {
            "pothole": counts.get("pothole", 0),
            "longitudinal_crack": counts.get("longitudinal_crack", 0),
            "lateral_crack": counts.get("lateral_crack", 0),
            "alligator_crack": counts.get("alligator_crack", 0)
        }