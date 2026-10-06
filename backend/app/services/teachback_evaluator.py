import json
import re
from typing import Dict, Any, Optional
from app.config import settings

class TeachBackEvaluator:
    """
    Evaluates a student's natural-language teach-back response using
    Gemini LLM (when configured) or a deterministic semantic rubric fallback.
    """

    @staticmethod
    async def evaluate_explanation(
        concept_name: str,
        concept_code: str,
        student_explanation: str,
        quiz_accuracy: float = 50.0
    ) -> Dict[str, Any]:
        """
        Evaluates the student's teach-back explanation across:
        - Accuracy (0-100)
        - Completeness (0-100)
        - Concept Coverage (0-100)
        - Misconception Detection (Boolean + details)
        - Example / Application (0-100)
        - Overall Score (0-100)
        """
        # Attempt Gemini LLM evaluation if API key is provided
        if settings.GEMINI_API_KEY:
            try:
                result = await TeachBackEvaluator._evaluate_with_llm(
                    concept_name, concept_code, student_explanation, quiz_accuracy
                )
                if result:
                    return result
            except Exception as e:
                print(f"[TeachBackEvaluator] LLM evaluation fallback triggered: {e}")

        # Deterministic semantic rubric fallback
        return TeachBackEvaluator._evaluate_deterministic(
            concept_name, concept_code, student_explanation, quiz_accuracy
        )

    @staticmethod
    async def _evaluate_with_llm(
        concept_name: str,
        concept_code: str,
        explanation: str,
        quiz_accuracy: float
    ) -> Optional[Dict[str, Any]]:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = f"""You are an expert Computer Science evaluator.
A student is explaining the concept: '{concept_name}' ({concept_code}) in their own words.

Student Explanation:
"{explanation}"

Student's recent quiz accuracy on this topic was: {quiz_accuracy:.0f}%.

Evaluate this explanation strictly based on these criteria:
1. Accuracy: Is the explanation technically correct? (0-100)
2. Completeness: Did they include the definition, mechanics, and why it works? (0-100)
3. Concept Coverage: Are the essential keywords and principles mentioned? (0-100)
4. Misconception: Did they state any incorrect facts or misunderstandings? (true/false)
5. Example: Did they provide or describe an example/application? (0-100)
6. Overall Score: Weighted score (0-100).
7. Feedback: 2-3 sentences of constructive mentoring.
8. Quiz vs TeachBack Insight: A comparison of how their teach-back aligns with their quiz performance.

Return ONLY a valid JSON object with these exact keys:
{{
  "accuracy": 75,
  "completeness": 65,
  "concept_coverage": 70,
  "misconception_detected": false,
  "misconception_details": "None",
  "example_score": 80,
  "overall_score": 72,
  "feedback": "...",
  "quiz_vs_teachback_insight": "..."
}}
"""
        response = await client.aio.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt
        )
        text = response.text.strip()
        # Extract JSON block if wrapped in markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        return json.loads(text)

    @staticmethod
    def _evaluate_deterministic(
        concept_name: str,
        concept_code: str,
        explanation: str,
        quiz_accuracy: float
    ) -> Dict[str, Any]:
        """
        Rule-based semantic parser for offline, deterministic grading.
        """
        clean_text = explanation.lower().strip()
        word_count = len(clean_text.split())

        # Keyword dictionaries for Python concepts
        key_concept_terms = {
            "PY-VAR": ["store", "memory", "value", "name", "assign", "="],
            "PY-COND": ["if", "else", "elif", "boolean", "true", "false", "condition"],
            "PY-LOOP": ["repeat", "iterate", "for", "while", "condition", "range"],
            "PY-FUNC": ["def", "call", "block", "reusable", "invoke", "execute"],
            "PY-PARAM": ["parameter", "argument", "pass", "input", "variable", "signature"],
            "PY-RET": ["return", "value", "caller", "output", "stack", "result"],
            "PY-BASE": ["base case", "stop", "terminate", "condition", "prevent", "infinite"],
            "PY-REC": ["calls itself", "base case", "recursive step", "stack", "smaller", "subproblem"]
        }

        # Check keyword matches
        expected_terms = key_concept_terms.get(concept_code, ["concept", "python", "code"])
        matched_terms = [t for t in expected_terms if t in clean_text]
        coverage_ratio = len(matched_terms) / max(len(expected_terms), 1)

        # Completeness based on length and depth
        completeness = min(100, int((word_count / 30) * 80) + int(coverage_ratio * 20))
        accuracy = min(100, 50 + int(coverage_ratio * 50))

        # Check for code example
        has_code_or_example = bool(re.search(r'(def\s+|return\s+|for\s+|if\s+|example|e\.g\.|such as|\d+)', clean_text))
        example_score = 85 if has_code_or_example else (40 if word_count > 25 else 20)

        # Misconception check: e.g. for return values vs print
        misconception_detected = False
        misconception_details = None
        if concept_code == "PY-RET" and "print" in clean_text and "return" not in clean_text:
            misconception_detected = True
            misconception_details = "Confused print() output with function return value."
            accuracy = max(30, accuracy - 25)
        elif concept_code == "PY-REC" and "base case" not in clean_text and "stop" not in clean_text:
            misconception_detected = True
            misconception_details = "Omitted the base case termination condition required to prevent infinite recursion."
            accuracy = max(35, accuracy - 20)

        overall = int((accuracy * 0.35) + (completeness * 0.25) + (int(coverage_ratio * 100) * 0.20) + (example_score * 0.20))

        # Quiz vs teachback comparison
        if quiz_accuracy >= 75 and overall < 55:
            insight = "High quiz accuracy but low teach-back depth indicates surface-level recall without deep conceptual mastery."
        elif quiz_accuracy < 55 and overall >= 70:
            insight = "Strong conceptual explanation despite quiz errors suggests simple calculation mistakes or test anxiety rather than a core gap."
        else:
            insight = f"Teach-back performance ({overall}%) corresponds consistently with demonstrated quiz performance ({quiz_accuracy:.0f}%)."

        return {
            "accuracy": accuracy,
            "completeness": completeness,
            "concept_coverage": int(coverage_ratio * 100),
            "misconception_detected": misconception_detected,
            "misconception_details": misconception_details or "No fundamental misconceptions detected.",
            "example_score": example_score,
            "overall_score": overall,
            "feedback": f"Good explanation. You captured {len(matched_terms)} key elements of {concept_name}." if overall >= 60 else f"Your explanation needs more technical precision. Focus on defining how {concept_name} operates step-by-step.",
            "quiz_vs_teachback_insight": insight
        }
