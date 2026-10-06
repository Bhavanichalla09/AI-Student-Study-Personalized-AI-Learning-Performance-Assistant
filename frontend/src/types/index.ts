// Core shared TypeScript interfaces for AI Student Study

export interface Student {
  id: string;
  name: string;
  email: string;
}

export interface Subject {
  id: string;
  name: string;
  description: string;
  topics_count?: number;
}

export interface Topic {
  id: string;
  subject_id: string;
  name: string;
  description?: string;
  sequence_order: number;
  concepts_count?: number;
}

export interface Concept {
  id: string;
  topic_id: string;
  code: string;
  name: string;
  description: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  sequence_order: number;
}

export interface PrerequisiteNode {
  id: string;
  name: string;
  code: string;
  mastery_score: number;
  mastery_level: 'strong' | 'developing' | 'critical';
  prerequisites: string[]; // IDs of prerequisites
}

export interface QuestionOption {
  id: string;
  text: string;
  misconception_tag?: string;
}

export interface Question {
  id: string;
  concept_id: string;
  concept_name?: string;
  question_text: string;
  options: QuestionOption[];
  difficulty: number;
}

export interface AttemptSubmission {
  session_id: string;
  question_id: string;
  concept_id: string;
  selected_option_id: string;
  confidence_score: number; // 0 to 100
  time_taken_seconds: number;
}

export interface AttemptResult {
  attempt_id: string;
  question_id: string;
  concept_id: string;
  is_correct: boolean;
  correct_option_id: string;
  explanation: string;
  confidence_score: number;
  misconception_detected?: string;
}

export interface QuizSessionSummary {
  session_id: string;
  topic_id: string;
  total_questions: number;
  correct_count: number;
  accuracy_percentage: number;
  avg_confidence: number;
  calibration_gap: number;
  attempts: AttemptResult[];
}

export interface MistakeItem {
  id: string;
  concept_id: string;
  concept_name: string;
  question_text: string;
  selected_answer: string;
  correct_answer: string;
  misconception_tag: string;
  is_repeated: boolean;
  repeat_count: number;
  root_cause_prerequisite?: string;
  diagnosis_level: 'HIGH CONFIDENCE' | 'LIKELY' | 'UNCERTAIN' | 'INSUFFICIENT EVIDENCE';
  explanation: string;
  timestamp: string;
}

export interface ConceptMastery {
  concept_id: string;
  concept_name: string;
  code: string;
  mastery_score: number; // 0 to 100
  mastery_level: 'strong' | 'developing' | 'critical';
  quiz_accuracy: number;
  teachback_score: number;
  prerequisite_health: number;
  confidence_avg: number;
  prerequisites: Array<{ id: string; name: string; mastery_score: number }>;
  why_evidence: Array<{
    type: string;
    description: string;
    is_positive: boolean;
  }>;
  diagnosis_confidence: number; // 0-100%
  diagnosis_state: 'HIGH CONFIDENCE' | 'LIKELY' | 'UNCERTAIN' | 'INSUFFICIENT EVIDENCE';
  recommended_action: string;
}

export interface TeachBackSubmission {
  concept_id: string;
  student_explanation: string;
}

export interface TeachBackResult {
  id: string;
  concept_id: string;
  accuracy: number;
  completeness: number;
  concept_coverage: number;
  misconception_detected: boolean;
  misconception_details?: string;
  example_score: number;
  overall_score: number;
  feedback: string;
  quiz_vs_teachback_insight: string;
}

export interface CalibrationDataPoint {
  concept_name: string;
  confidence: number;
  accuracy: number;
  gap: number;
  category: 'overconfident' | 'underconfident' | 'well_calibrated';
  sample_size: number;
}

export interface CalibrationSummary {
  overall_avg_confidence: number;
  overall_avg_accuracy: number;
  calibration_gap: number;
  primary_bias: 'Overconfidence' | 'Underconfidence' | 'Calibrated';
  data_points: CalibrationDataPoint[];
  insight_explanation: string;
}

export interface Recommendation {
  id: string;
  concept_id: string;
  concept_name: string;
  root_cause_concept_id?: string;
  root_cause_concept_name?: string;
  title: string;
  reason: string;
  action_steps: string[];
  priority: 'high' | 'medium' | 'low';
  is_completed: boolean;
}
