from collections import Counter


class SeverityAnalyzer:

    @staticmethod
    def classify(area):
        """
        Classify severity based on detected damage area
        """

        if area < 5000:
            return "Low"

        elif area < 20000:
            return "Medium"

        return "High"

    @staticmethod
    def analyze(detection):
        """
        Analyze a single detection
        """

        severity = SeverityAnalyzer.classify(
            detection["area"]
        )

        return {
            "class_name": detection["class_name"],
            "confidence": detection["confidence"],
            "area": detection["area"],
            "severity": severity
        }

    @staticmethod
    def summarize(detections):
        """
        Generate severity summary
        """

        levels = []

        for d in detections:

            levels.append(
                SeverityAnalyzer.classify(
                    d["area"]
                )
            )

        counts = Counter(levels)

        return {
            "High": counts.get("High", 0),
            "Medium": counts.get("Medium", 0),
            "Low": counts.get("Low", 0)
        }