from src.app.database_manager import DatabaseManager


class Analytics:

    def __init__(self):

        self.db = DatabaseManager()

    def total_records(self):

        return len(
            self.db.get_all_detections()
        )

    def total_potholes(self):

        rows = self.db.get_all_detections()

        return sum(row[2] for row in rows)

    def total_high_risk(self):

        rows = self.db.get_all_detections()

        return sum(row[6] for row in rows)