class RoadDamageRanker:
    @staticmethod
    def calculate_damage_score(potholes, long_cracks, lat_cracks, alligator_cracks):
        """
        Calculate Road Damage Score (RDS) from 0 to 100 based on detected defects.
        Weights:
        - Alligator Crack (structural/fatigue failure): 20
        - Pothole (safety hazard/impact risk): 15
        - Longitudinal Crack: 5
        - Lateral Crack: 5
        """
        score = (
            (alligator_cracks * 20) +
            (potholes * 15) +
            (long_cracks * 5) +
            (lat_cracks * 5)
        )
        return min(100, int(score))

    @staticmethod
    def get_priority_category(score):
        """
        Map score to Priority Rank.
        - 0-20: Low (Green) - Routine maintenance
        - 21-50: Medium (Yellow) - Scheduled intervention (90 days)
        - 51-100: Critical (Red) - Urgent repair dispatch
        """
        if score <= 20:
            return "Low"
        elif score <= 50:
            return "Medium"
        return "Critical"
