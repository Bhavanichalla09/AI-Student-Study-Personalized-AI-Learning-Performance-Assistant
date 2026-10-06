from typing import Dict, Any

class CalibrationEngine:
    """
    Calculates the mathematical calibration between a student's
    subjective confidence (0-100%) and objective accuracy (0-100%).
    """

    OVERCONFIDENCE_THRESHOLD = 15.0
    UNDERCONFIDENCE_THRESHOLD = -15.0

    @staticmethod
    def calculate_gap(avg_confidence: float, avg_accuracy: float) -> float:
        """Gap = Confidence - Accuracy. Positive = Overconfidence, Negative = Underconfidence."""
        return round(avg_confidence - avg_accuracy, 1)

    @staticmethod
    def classify_calibration(gap: float) -> str:
        """Classifies the calibration category."""
        if gap > CalibrationEngine.OVERCONFIDENCE_THRESHOLD:
            return "overconfident"
        elif gap < CalibrationEngine.UNDERCONFIDENCE_THRESHOLD:
            return "underconfident"
        return "well_calibrated"

    @staticmethod
    def generate_insight(avg_confidence: float, avg_accuracy: float, category: str) -> str:
        """Generates clear, pedagogical feedback explaining the calibration state."""
        if category == "overconfident":
            return (
                f"You reported an average confidence of {avg_confidence:.0f}%, but achieved an accuracy of {avg_accuracy:.0f}%. "
                f"This indicates overconfidence: you feel certain of your answers, but subtle misconceptions or missed edge cases are occurring."
            )
        elif category == "underconfident":
            return (
                f"You demonstrated strong accuracy ({avg_accuracy:.0f}%), yet your average reported confidence was only {avg_confidence:.0f}%. "
                f"You know more than you think! Trust your conceptual instincts and practice solving problems without second-guessing."
            )
        else:
            return (
                f"Your confidence ({avg_confidence:.0f}%) is well-aligned with your actual accuracy ({avg_accuracy:.0f}%). "
                f"You have accurate metacognitive awareness of what you know and what you need to review."
            )
