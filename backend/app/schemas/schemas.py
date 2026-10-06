from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

# Base
class StudentResponse(BaseModel):
    id: str
    email: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)

class SubjectResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    topics_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class TopicResponse(BaseModel):
    id: str
    subject_id: str
    name: str
    description: Optional[str] = None
    sequence_order: int
    concepts_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class ConceptResponse(BaseModel):
    id: str
    topic_id: str
    code: str
    name: str
    description: Optional[str] = None
    difficulty_level: str
    sequence_order: int

    model_config = ConfigDict(from_attributes=True)

class PrerequisiteEdge(BaseModel):
    concept_id: str
    prerequisite_concept_id: str
    relationship_type: str

class QuestionOptionSchema(BaseModel):
    id: str
    text: str
    misconception_tag: Optional[str] = None

class QuestionResponse(BaseModel):
    id: str
    concept_id: str
    concept_name: Optional[str] = None
    question_text: str
    options: List[QuestionOptionSchema]
    difficulty: int

    model_config = ConfigDict(from_attributes=True)

# Quiz Schemas
class QuizStartRequest(BaseModel):
    topic_id: str
    student_id: Optional[str] = None

class QuizStartResponse(BaseModel):
    session_id: str
    topic_id: str
    student_id: str
    questions: List[QuestionResponse]

class AttemptSubmitRequest(BaseModel):
    session_id: str
    question_id: str
    concept_id: str
    selected_option_id: str
    confidence_score: int = Field(ge=0, le=100) # 0 to 100
    time_taken_seconds: int = 0
    student_id: Optional[str] = None

class AttemptResultResponse(BaseModel):
    attempt_id: str
    question_id: str
    concept_id: str
    is_correct: bool
    correct_option_id: str
    explanation: Optional[str] = None
    confidence_score: int
    misconception_detected: Optional[str] = None

class QuizSessionSummaryResponse(BaseModel):
    session_id: str
    topic_id: str
    total_questions: int
    correct_count: int
    accuracy_percentage: float
    avg_confidence: float
    calibration_gap: float
    attempts: List[AttemptResultResponse]

# Mistake Schemas
class MistakeResponse(BaseModel):
    id: str
    concept_id: str
    concept_name: str
    question_text: str
    selected_answer: str
    correct_answer: str
    misconception_tag: str
    is_repeated: bool
    repeat_count: int
    root_cause_prerequisite: Optional[str] = None
    diagnosis_level: str
    explanation: str
    timestamp: str

# Teach-Back Schemas
class TeachBackSubmitRequest(BaseModel):
    concept_id: str
    student_explanation: str
    student_id: Optional[str] = None

class TeachBackResponse(BaseModel):
    id: str
    concept_id: str
    accuracy: int
    completeness: int
    concept_coverage: int
    misconception_detected: bool
    misconception_details: Optional[str] = None
    example_score: int
    overall_score: int
    feedback: str
    quiz_vs_teachback_insight: str

# Knowledge Map & Evidence Schemas
class WhyEvidenceItem(BaseModel):
    type: str
    description: str
    is_positive: bool

class ConceptMasteryItem(BaseModel):
    concept_id: str
    concept_name: str
    code: str
    mastery_score: float
    mastery_level: str # strong, developing, critical
    quiz_accuracy: float
    teachback_score: float
    prerequisite_health: float
    confidence_avg: float
    prerequisites: List[Dict[str, Any]]
    why_evidence: List[WhyEvidenceItem]
    diagnosis_confidence: float
    diagnosis_state: str # HIGH CONFIDENCE, LIKELY, UNCERTAIN, INSUFFICIENT EVIDENCE
    recommended_action: str

class KnowledgeMapResponse(BaseModel):
    topic_id: str
    student_id: str
    overall_mastery: float
    concepts: List[ConceptMasteryItem]

# Confidence Calibration
class CalibrationDataPoint(BaseModel):
    concept_name: str
    confidence: float
    accuracy: float
    gap: float
    category: str # overconfident, underconfident, well_calibrated
    sample_size: int

class CalibrationSummaryResponse(BaseModel):
    overall_avg_confidence: float
    overall_avg_accuracy: float
    calibration_gap: float
    primary_bias: str
    data_points: List[CalibrationDataPoint]
    insight_explanation: str

# Recommendations
class RecommendationResponse(BaseModel):
    id: str
    concept_id: str
    concept_name: str
    root_cause_concept_id: Optional[str] = None
    root_cause_concept_name: Optional[str] = None
    title: str
    reason: str
    action_steps: List[str]
    priority: str
    is_completed: bool

class RetestRequest(BaseModel):
    concept_id: str
    student_id: Optional[str] = None

class RetestResponse(BaseModel):
    session_id: str
    concept_id: str
    questions: List[QuestionResponse]
