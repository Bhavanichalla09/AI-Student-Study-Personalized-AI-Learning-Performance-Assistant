import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("DiagnosticSession", back_populates="student")
    attempts = relationship("Attempt", back_populates="student")
    mastery_states = relationship("MasteryState", back_populates="student")
    teachback_attempts = relationship("TeachBackAttempt", back_populates="student")
    recommendations = relationship("Recommendation", back_populates="student")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subject = relationship("Subject", back_populates="topics")
    concepts = relationship("Concept", back_populates="topic", cascade="all, delete-orphan")


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(50), default="beginner") # beginner, intermediate, advanced
    sequence_order = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="concepts")
    questions = relationship("Question", back_populates="concept")
    prerequisites = relationship(
        "Prerequisite",
        foreign_keys="[Prerequisite.concept_id]",
        back_populates="concept",
        cascade="all, delete-orphan"
    )


class Prerequisite(Base):
    """
    Represents directed graph edge:
    concept_id DEPENDS ON prerequisite_concept_id
    """
    __tablename__ = "prerequisites"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    prerequisite_concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(50), default="direct_prerequisite")
    weight = Column(Float, default=1.0) # Strength of dependency

    # Relationships
    concept = relationship("Concept", foreign_keys=[concept_id], back_populates="prerequisites")
    prerequisite_concept = relationship("Concept", foreign_keys=[prerequisite_concept_id])


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False) # List of dicts: [{"id": "A", "text": "...", "misconception_tag": "..."}]
    correct_option_id = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(Integer, default=1) # 1 to 5
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    concept = relationship("Concept", back_populates="questions")
    attempts = relationship("Attempt", back_populates="question")


class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="in_progress") # in_progress, completed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="sessions")
    attempts = relationship("Attempt", back_populates="session", cascade="all, delete-orphan")


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("diagnostic_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_option_id = Column(String(10), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    confidence_score = Column(Integer, nullable=False) # 0 to 100
    time_taken_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("DiagnosticSession", back_populates="attempts")
    student = relationship("Student", back_populates="attempts")
    question = relationship("Question", back_populates="attempts")
    mistake = relationship("Mistake", back_populates="attempt", uselist=False, cascade="all, delete-orphan")


class Mistake(Base):
    __tablename__ = "mistakes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, unique=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    misconception_tag = Column(String(100), nullable=False, index=True)
    is_repeated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attempt = relationship("Attempt", back_populates="mistake")


class TeachBackAttempt(Base):
    __tablename__ = "teachback_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt_text = Column(Text, nullable=False)
    student_response = Column(Text, nullable=False)
    accuracy_score = Column(Integer, nullable=False) # 0-100
    completeness_score = Column(Integer, nullable=False) # 0-100
    concept_coverage_score = Column(Integer, nullable=False) # 0-100
    misconception_detected = Column(Boolean, default=False)
    misconception_details = Column(Text, nullable=True)
    example_score = Column(Integer, default=0) # 0-100
    overall_score = Column(Integer, nullable=False) # 0-100
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="teachback_attempts")


class ConfidenceMetric(Base):
    __tablename__ = "confidence_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    avg_confidence = Column(Float, nullable=False)
    avg_accuracy = Column(Float, nullable=False)
    calibration_gap = Column(Float, nullable=False) # avg_confidence - avg_accuracy
    calibration_category = Column(String(50), nullable=False) # overconfident, underconfident, well_calibrated
    sample_count = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MasteryState(Base):
    __tablename__ = "mastery_states"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0) # 0.0 to 100.0
    mastery_level = Column(String(50), default="critical") # strong, developing, critical
    quiz_weight = Column(Float, default=0.40)
    recent_weight = Column(Float, default=0.20)
    teachback_weight = Column(Float, default=0.20)
    prerequisite_weight = Column(Float, default=0.10)
    history_weight = Column(Float, default=0.10)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="mastery_states")


class DiagnosticEvidence(Base):
    __tablename__ = "diagnostic_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("diagnostic_sessions.id", ondelete="SET NULL"), nullable=True)
    evidence_type = Column(String(50), nullable=False) # quiz_performance, repeated_mistake, prerequisite_gap, teachback_result, confidence_calibration
    evidence_value = Column(JSON, nullable=True)
    signal_weight = Column(Float, default=1.0)
    confidence_level = Column(String(50), default="LIKELY") # HIGH CONFIDENCE, LIKELY, UNCERTAIN, INSUFFICIENT EVIDENCE
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    target_concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    root_cause_concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    action_steps = Column(JSON, nullable=False) # List of string instructions
    priority = Column(String(20), default="high") # high, medium, low
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="recommendations")


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    session_type = Column(String(50), default="diagnostic") # diagnostic, remediation, retest
    summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
