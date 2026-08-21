from typing import List

class RecommendationEngine:
    """
    Generates personalized, actionable study recommendations and wellbeing tips
    tailored to the student's current Focus Score, Burnout Risk, and behavior trends.
    """

    def generate_recommendations(
        self,
        focus_score: float,
        burnout_score: float,
        attendance_rate: float,
        entertainment_mins: int
    ) -> List[str]:
        recommendations = []

        if burnout_score > 70.0:
            recommendations.append("High Burnout Alert: Take a 45-minute screen-free break and aim for 8 hours of sleep tonight.")
            recommendations.append("Schedule a meeting with your academic mentor to adjust your workload.")
        elif burnout_score > 45.0:
            recommendations.append("Moderate Fatigue Detected: Implement 25-minute Pomodoro study blocks with 5-minute movement breaks.")

        if focus_score < 60.0:
            recommendations.append("Focus Enhancement: Enable Website Blocker for Social Media & YouTube during active study hours.")
            recommendations.append("Try pairing coding tasks with instrumental focus playlists.")

        if entertainment_mins > 120:
            recommendations.append(f"Distraction Advisory: You spent {entertainment_mins} minutes on entertainment today. Set daily app limits.")

        if attendance_rate < 80.0:
            recommendations.append("Attendance Recovery: Your course attendance is below 80%. Review upcoming lectures to avoid exam disqualification.")

        if len(recommendations) < 3:
            recommendations.append("Maintain Momentum: Excellent focus stability! Keep up the structured study routine.")
            recommendations.append("Digital Wellness Tip: Remember to look away from your screen every 20 minutes (20-20-20 rule).")

        return recommendations[:4]

recommendation_engine = RecommendationEngine()
