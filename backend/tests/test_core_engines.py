import pytest
from app.services.calibration_engine import CalibrationEngine
from app.services.mastery_service import MasteryService

def test_calibration_calculations():
    # Overconfidence check
    gap_over = CalibrationEngine.calculate_gap(90.0, 45.0)
    assert gap_over == 45.0
    assert CalibrationEngine.classify_calibration(gap_over) == "overconfident"

    # Underconfidence check
    gap_under = CalibrationEngine.calculate_gap(40.0, 85.0)
    assert gap_under == -45.0
    assert CalibrationEngine.classify_calibration(gap_under) == "underconfident"

    # Well-calibrated check
    gap_well = CalibrationEngine.calculate_gap(75.0, 70.0)
    assert gap_well == 5.0
    assert CalibrationEngine.classify_calibration(gap_well) == "well_calibrated"

def test_mastery_classification():
    assert MasteryService.classify_mastery_level(95.0) == "strong"
    assert MasteryService.classify_mastery_level(80.0) == "strong"
    assert MasteryService.classify_mastery_level(79.9) == "developing"
    assert MasteryService.classify_mastery_level(50.0) == "developing"
    assert MasteryService.classify_mastery_level(49.9) == "critical"
    assert MasteryService.classify_mastery_level(15.0) == "critical"

def test_calibration_insight_message():
    insight = CalibrationEngine.generate_insight(90.0, 45.0, "overconfident")
    assert "overconfidence" in insight.lower()
    assert "90%" in insight
    assert "45%" in insight
