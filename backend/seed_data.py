import asyncio
from datetime import datetime, timedelta
from app.database import AsyncSessionLocal, engine, Base
from app.models import (
    Student, Subject, Topic, Concept, Prerequisite,
    Question, DiagnosticSession, Attempt, Mistake,
    TeachBackAttempt, ConfidenceMetric, MasteryState,
    DiagnosticEvidence, Recommendation
)

async def seed_database():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        from sqlalchemy import select
        res = await session.execute(select(Subject).filter_by(slug="python-programming"))
        if res.scalar_one_or_none():
            print("Database already contains seed data. Skipping re-seed.")
            return

        print("Seeding fresh data for AI Student Study...")

        # 1. Student
        student = Student(
            id="student_demo_1",
            email="rahul.sharma@college.edu",
            full_name="Rahul Sharma"
        )
        session.add(student)

        # 2. Subject
        subject = Subject(
            id="subject_py",
            name="Python Programming",
            slug="python-programming",
            description="Core concepts from basic syntax to advanced recursion and call stack mechanics."
        )
        session.add(subject)

        # 3. Topic
        topic = Topic(
            id="topic_func_rec",
            subject_id=subject.id,
            name="Functions & Recursion",
            description="Mastering function signatures, parameter passing, return value stack frames, and recursive logic.",
            sequence_order=1
        )
        session.add(topic)

        # 4. Concepts
        c_var = Concept(
            id="c_var",
            topic_id=topic.id,
            code="PY-VAR",
            name="Variables & Scope",
            description="Variable assignment, lifetime, local vs global scope in Python.",
            difficulty_level="beginner",
            sequence_order=1
        )
        c_cond = Concept(
            id="c_cond",
            topic_id=topic.id,
            code="PY-COND",
            name="Conditionals & Boolean Logic",
            description="Truth values, if-elif-else branches, comparison operators.",
            difficulty_level="beginner",
            sequence_order=2
        )
        c_loop = Concept(
            id="c_loop",
            topic_id=topic.id,
            code="PY-LOOP",
            name="Iteration & Loops",
            description="For loops, while loops, range generation, and loop termination.",
            difficulty_level="beginner",
            sequence_order=3
        )
        c_func = Concept(
            id="c_func",
            topic_id=topic.id,
            code="PY-FUNC",
            name="Function Definitions & Calls",
            description="Defining reusable blocks with def, invocation syntax, execution jumping.",
            difficulty_level="intermediate",
            sequence_order=4
        )
        c_param = Concept(
            id="c_param",
            topic_id=topic.id,
            code="PY-PARAM",
            name="Parameters & Arguments",
            description="Positional vs keyword arguments, default parameters, formal parameter binding.",
            difficulty_level="intermediate",
            sequence_order=5
        )
        c_ret = Concept(
            id="c_ret",
            topic_id=topic.id,
            code="PY-RET",
            name="Return Values & Stack Propagation",
            description="Function output via return statement, returning vs printing, call stack frames.",
            difficulty_level="intermediate",
            sequence_order=6
        )
        c_base = Concept(
            id="c_base",
            topic_id=topic.id,
            code="PY-BASE",
            name="Base Case Termination",
            description="Stopping conditions in recursive logic to avoid infinite recursion stack overflows.",
            difficulty_level="advanced",
            sequence_order=7
        )
        c_rec = Concept(
            id="c_rec",
            topic_id=topic.id,
            code="PY-REC",
            name="Recursive Step & Call Stack",
            description="Self-referential functions, breaking problems into smaller subproblems, stack unwinding.",
            difficulty_level="advanced",
            sequence_order=8
        )

        concepts = [c_var, c_cond, c_loop, c_func, c_param, c_ret, c_base, c_rec]
        session.add_all(concepts)
        await session.flush()

        # 5. Prerequisite Edges (Directed Graph)
        prereqs = [
            # Functions require Variables and Conditionals
            Prerequisite(concept_id=c_func.id, prerequisite_concept_id=c_var.id, weight=1.0),
            Prerequisite(concept_id=c_func.id, prerequisite_concept_id=c_cond.id, weight=1.0),
            # Parameters require Functions
            Prerequisite(concept_id=c_param.id, prerequisite_concept_id=c_func.id, weight=1.0),
            # Return Values require Parameters and Functions
            Prerequisite(concept_id=c_ret.id, prerequisite_concept_id=c_param.id, weight=1.0),
            Prerequisite(concept_id=c_ret.id, prerequisite_concept_id=c_func.id, weight=1.0),
            # Base Case requires Conditionals and Return Values
            Prerequisite(concept_id=c_base.id, prerequisite_concept_id=c_cond.id, weight=1.0),
            Prerequisite(concept_id=c_base.id, prerequisite_concept_id=c_ret.id, weight=1.0),
            # Recursion requires Base Case and Return Values
            Prerequisite(concept_id=c_rec.id, prerequisite_concept_id=c_base.id, weight=1.0),
            Prerequisite(concept_id=c_rec.id, prerequisite_concept_id=c_ret.id, weight=1.0),
        ]
        session.add_all(prereqs)

        # 6. Diagnostic Questions with Misconception Tags
        questions = [
            # Q1: Variables
            Question(
                id="q_var_1",
                concept_id=c_var.id,
                question_text="Consider this code:\n```python\nx = 10\ndef update():\n    x = 20\nupdate()\nprint(x)\n```\nWhat does this print?",
                options=[
                    {"id": "A", "text": "10", "misconception_tag": "correct"},
                    {"id": "B", "text": "20", "misconception_tag": "confusing_local_and_global_scope"},
                    {"id": "C", "text": "None", "misconception_tag": "assuming_function_replaces_variable_with_none"},
                    {"id": "D", "text": "Error", "misconception_tag": "unbound_local_misconception"}
                ],
                correct_option_id="A",
                explanation="In Python, assigning x = 20 inside update() creates a local variable x. The global x remains 10.",
                difficulty=1
            ),
            # Q2: Conditionals
            Question(
                id="q_cond_1",
                concept_id=c_cond.id,
                question_text="What will be the output of:\n```python\na = []\nif a:\n    print('True')\nelse:\n    print('False')\n```",
                options=[
                    {"id": "A", "text": "True", "misconception_tag": "assuming_empty_container_is_truthy"},
                    {"id": "B", "text": "False", "misconception_tag": "correct"},
                    {"id": "C", "text": "TypeError", "misconception_tag": "expecting_strict_boolean_type"},
                    {"id": "D", "text": "None", "misconception_tag": "general_syntax_misconception"}
                ],
                correct_option_id="B",
                explanation="In Python, empty collections (empty list [], empty string '', 0) evaluate to False in a boolean context.",
                difficulty=1
            ),
            # Q3: Loops
            Question(
                id="q_loop_1",
                concept_id=c_loop.id,
                question_text="How many times will 'Python' print?\n```python\nfor i in range(1, 6, 2):\n    print('Python')\n```",
                options=[
                    {"id": "A", "text": "3 times (for 1, 3, 5)", "misconception_tag": "correct"},
                    {"id": "B", "text": "2 times (for 1, 3)", "misconception_tag": "off_by_one_step_calculation"},
                    {"id": "C", "text": "5 times", "misconception_tag": "ignoring_step_argument"},
                    {"id": "D", "text": "6 times", "misconception_tag": "including_stop_boundary"}
                ],
                correct_option_id="A",
                explanation="range(1, 6, 2) starts at 1, steps by 2, and stops before 6: produces 1, 3, 5 (3 iterations).",
                difficulty=1
            ),
            # Q4: Function Definition
            Question(
                id="q_func_1",
                concept_id=c_func.id,
                question_text="What does a Python function return if there is no explicit `return` statement in its body?",
                options=[
                    {"id": "A", "text": "0", "misconception_tag": "assuming_c_style_zero_return"},
                    {"id": "B", "text": "None", "misconception_tag": "correct"},
                    {"id": "C", "text": "False", "misconception_tag": "assuming_boolean_false_default"},
                    {"id": "D", "text": "It throws an error", "misconception_tag": "expecting_mandatory_return"}
                ],
                correct_option_id="B",
                explanation="In Python, functions without an explicit return statement implicitly return None.",
                difficulty=2
            ),
            # Q5: Parameters
            Question(
                id="q_param_1",
                concept_id=c_param.id,
                question_text="Given this function definition:\n```python\ndef greet(name, msg='Hello'):\n    return f'{msg}, {name}!'\n```\nWhat is the result of `greet('Bob')`?",
                options=[
                    {"id": "A", "text": "'Hello, Bob!'", "misconception_tag": "correct"},
                    {"id": "B", "text": "'Bob, Hello!'", "misconception_tag": "confusing_parameter_binding_order"},
                    {"id": "C", "text": "TypeError: missing required argument", "misconception_tag": "unaware_of_default_arguments"},
                    {"id": "D", "text": "None", "misconception_tag": "general_syntax_misconception"}
                ],
                correct_option_id="A",
                explanation="'Bob' binds to the first positional parameter 'name'. The second parameter 'msg' defaults to 'Hello'.",
                difficulty=2
            ),
            # Q6: Return Values (Crucial Prerequisite)
            Question(
                id="q_ret_1",
                concept_id=c_ret.id,
                question_text="Look at this function:\n```python\ndef add(a, b):\n    print(a + b)\n\nresult = add(3, 4)\nprint(result)\n```\nWhat is printed by `print(result)`?",
                options=[
                    {"id": "A", "text": "7", "misconception_tag": "confusing_print_with_return"},
                    {"id": "B", "text": "None", "misconception_tag": "correct"},
                    {"id": "C", "text": "0", "misconception_tag": "assuming_default_numeric_return"},
                    {"id": "D", "text": "Error: add does not produce value", "misconception_tag": "syntax_error_misconception"}
                ],
                correct_option_id="B",
                explanation="add() uses print(), which displays 7 on the console but returns None. Thus, result receives None.",
                difficulty=2
            ),
            # Q7: Return Values (Chained Propagation)
            Question(
                id="q_ret_2",
                concept_id=c_ret.id,
                question_text="What is the output of:\n```python\ndef double(x):\n    return x * 2\n\ndef quad(x):\n    double(double(x))\n\nprint(quad(3))\n```",
                options=[
                    {"id": "A", "text": "12", "misconception_tag": "assuming_implicit_last_expression_return"},
                    {"id": "B", "text": "None", "misconception_tag": "correct"},
                    {"id": "C", "text": "6", "misconception_tag": "evaluating_only_inner_function"},
                    {"id": "D", "text": "24", "misconception_tag": "arithmetic_error"}
                ],
                correct_option_id="B",
                explanation="quad() calls double(double(x)) which computes 12, but quad() forgets to `return` it! Hence quad(3) returns None.",
                difficulty=3
            ),
            # Q8: Base Case Termination
            Question(
                id="q_base_1",
                concept_id=c_base.id,
                question_text="What happens if a recursive function does NOT have a valid base case?",
                options=[
                    {"id": "A", "text": "It executes once and exits", "misconception_tag": "assuming_single_pass_fallback"},
                    {"id": "B", "text": "RecursionError: maximum recursion depth exceeded", "misconception_tag": "correct"},
                    {"id": "C", "text": "The computer reboots", "misconception_tag": "hardware_misconception"},
                    {"id": "D", "text": "It returns None automatically", "misconception_tag": "assuming_automatic_termination"}
                ],
                correct_option_id="B",
                explanation="Without a base case condition to halt the recursion, the function calls itself indefinitely until Python exceeds the recursion stack limit.",
                difficulty=2
            ),
            # Q9: Recursion (The Target Evaluation Question)
            Question(
                id="q_rec_1",
                concept_id=c_rec.id,
                question_text="Trace this recursive function:\n```python\ndef mystery(n):\n    if n <= 1:\n        return 1\n    return n + mystery(n - 1)\n\nprint(mystery(4))\n```\nWhat is the output?",
                options=[
                    {"id": "A", "text": "10", "misconception_tag": "correct"},
                    {"id": "B", "text": "4", "misconception_tag": "ignoring_recursive_stack_accumulation"},
                    {"id": "C", "text": "None", "misconception_tag": "confusing_print_with_return"},
                    {"id": "D", "text": "24", "misconception_tag": "confusing_sum_with_factorial"}
                ],
                correct_option_id="A",
                explanation="mystery(4) = 4 + mystery(3) = 4 + (3 + mystery(2)) = 4 + 3 + (2 + mystery(1)) = 4 + 3 + 2 + 1 = 10.",
                difficulty=3
            ),
            # Q10: Recursion (Return Propagation Bug)
            Question(
                id="q_rec_2",
                concept_id=c_rec.id,
                question_text="What does this function return?\n```python\ndef countdown(n):\n    if n == 0:\n        return 'Done'\n    countdown(n - 1)\n\nans = countdown(3)\nprint(ans)\n```",
                options=[
                    {"id": "A", "text": "'Done'", "misconception_tag": "assuming_recursive_call_automatically_propagates_return"},
                    {"id": "B", "text": "None", "misconception_tag": "correct"},
                    {"id": "C", "text": "0", "misconception_tag": "returning_base_case_argument"},
                    {"id": "D", "text": "3", "misconception_tag": "returning_initial_argument"}
                ],
                correct_option_id="B",
                explanation="Crucial Python trap! countdown(n-1) is invoked without `return countdown(n-1)`. The returned 'Done' is dropped, returning None to the caller.",
                difficulty=3
            )
        ]
        session.add_all(questions)
        await session.flush()

        # 7. Seed Rahul's Realistic Diagnostic Session & Learner State
        # Scenario: Rahul completed a diagnostic session earlier.
        # He aced Variables (100%), Conditions (100%), Loops (100%), and Functions (100%).
        # BUT he repeatedly failed Return Values (q_ret_1 and q_ret_2) by confusing print with return.
        # When he reached Recursion (q_rec_1 and q_rec_2), he reported HIGH CONFIDENCE (90%) but failed both!
        now = datetime.utcnow()
        session_1 = DiagnosticSession(
            id="session_demo_1",
            student_id=student.id,
            topic_id=topic.id,
            status="completed",
            started_at=now - timedelta(hours=2),
            completed_at=now - timedelta(hours=1, minutes=45)
        )
        session.add(session_1)
        await session.flush()

        demo_attempts = [
            # High performance on fundamentals
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_var_1", concept_id=c_var.id, selected_option_id="A", is_correct=True, confidence_score=95, time_taken_seconds=12),
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_cond_1", concept_id=c_cond.id, selected_option_id="B", is_correct=True, confidence_score=90, time_taken_seconds=15),
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_loop_1", concept_id=c_loop.id, selected_option_id="A", is_correct=True, confidence_score=85, time_taken_seconds=20),
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_func_1", concept_id=c_func.id, selected_option_id="B", is_correct=True, confidence_score=80, time_taken_seconds=18),
            # Parameter struggle
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_param_1", concept_id=c_param.id, selected_option_id="B", is_correct=False, confidence_score=65, time_taken_seconds=30),
            # Return Values (FAILED - repeated mistake confusing print with return)
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_ret_1", concept_id=c_ret.id, selected_option_id="A", is_correct=False, confidence_score=85, time_taken_seconds=25),
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_ret_2", concept_id=c_ret.id, selected_option_id="A", is_correct=False, confidence_score=80, time_taken_seconds=35),
            # Base Case
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_base_1", concept_id=c_base.id, selected_option_id="B", is_correct=True, confidence_score=75, time_taken_seconds=15),
            # Recursion (FAILED - Severe Overconfidence: 90% confidence, selected wrong!)
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_rec_1", concept_id=c_rec.id, selected_option_id="C", is_correct=False, confidence_score=90, time_taken_seconds=40),
            Attempt(session_id=session_1.id, student_id=student.id, question_id="q_rec_2", concept_id=c_rec.id, selected_option_id="A", is_correct=False, confidence_score=85, time_taken_seconds=45),
        ]
        session.add_all(demo_attempts)
        await session.flush()

        # Seed Mistakes for the failed attempts
        mistakes = [
            Mistake(attempt_id=demo_attempts[4].id, student_id=student.id, concept_id=c_param.id, misconception_tag="confusing_parameter_binding_order", is_repeated=False),
            Mistake(attempt_id=demo_attempts[5].id, student_id=student.id, concept_id=c_ret.id, misconception_tag="confusing_print_with_return", is_repeated=False),
            Mistake(attempt_id=demo_attempts[6].id, student_id=student.id, concept_id=c_ret.id, misconception_tag="confusing_print_with_return", is_repeated=True), # REPEATED!
            Mistake(attempt_id=demo_attempts[8].id, student_id=student.id, concept_id=c_rec.id, misconception_tag="confusing_print_with_return", is_repeated=True),
            Mistake(attempt_id=demo_attempts[9].id, student_id=student.id, concept_id=c_rec.id, misconception_tag="assuming_recursive_call_automatically_propagates_return", is_repeated=False)
        ]
        session.add_all(mistakes)

        # Seed Teach-Back Attempt for Return Values (Shows student missed return value propagation)
        tb = TeachBackAttempt(
            student_id=student.id,
            concept_id=c_ret.id,
            prompt_text="Explain in your own words how return values pass information back to the function caller.",
            student_response="A function prints the value on the terminal so that the next line of code can read it from the screen.",
            accuracy_score=40,
            completeness_score=45,
            concept_coverage_score=35,
            misconception_detected=True,
            misconception_details="Confused console print() stdout with the call stack return value mechanism.",
            example_score=30,
            overall_score=42,
            feedback="You are confusing printing to the terminal with returning a value to the caller. print() is for humans; return is for code."
        )
        session.add(tb)

        # Seed Confidence Metrics
        session.add(ConfidenceMetric(student_id=student.id, concept_id=c_var.id, avg_confidence=95.0, avg_accuracy=100.0, calibration_gap=-5.0, calibration_category="well_calibrated", sample_count=1))
        session.add(ConfidenceMetric(student_id=student.id, concept_id=c_cond.id, avg_confidence=90.0, avg_accuracy=100.0, calibration_gap=-10.0, calibration_category="well_calibrated", sample_count=1))
        session.add(ConfidenceMetric(student_id=student.id, concept_id=c_loop.id, avg_confidence=85.0, avg_accuracy=100.0, calibration_gap=-15.0, calibration_category="well_calibrated", sample_count=1))
        session.add(ConfidenceMetric(student_id=student.id, concept_id=c_func.id, avg_confidence=80.0, avg_accuracy=100.0, calibration_gap=-20.0, calibration_category="underconfident", sample_count=1))
        session.add(ConfidenceMetric(student_id=student.id, concept_id=c_param.id, avg_confidence=65.0, avg_accuracy=0.0, calibration_gap=65.0, calibration_category="overconfident", sample_count=1))
        session.add(ConfidenceMetric(student_id=student.id, concept_id=c_ret.id, avg_confidence=82.5, avg_accuracy=0.0, calibration_gap=82.5, calibration_category="overconfident", sample_count=2))
        session.add(ConfidenceMetric(student_id=student.id, concept_id=c_base.id, avg_confidence=75.0, avg_accuracy=100.0, calibration_gap=-25.0, calibration_category="underconfident", sample_count=1))
        session.add(ConfidenceMetric(student_id=student.id, concept_id=c_rec.id, avg_confidence=87.5, avg_accuracy=0.0, calibration_gap=87.5, calibration_category="overconfident", sample_count=2))

        # Seed Initial Mastery States
        session.add(MasteryState(student_id=student.id, concept_id=c_var.id, mastery_score=94.0, mastery_level="strong"))
        session.add(MasteryState(student_id=student.id, concept_id=c_cond.id, mastery_score=88.0, mastery_level="strong"))
        session.add(MasteryState(student_id=student.id, concept_id=c_loop.id, mastery_score=72.0, mastery_level="developing"))
        session.add(MasteryState(student_id=student.id, concept_id=c_func.id, mastery_score=68.0, mastery_level="developing"))
        session.add(MasteryState(student_id=student.id, concept_id=c_param.id, mastery_score=48.0, mastery_level="critical"))
        session.add(MasteryState(student_id=student.id, concept_id=c_ret.id, mastery_score=36.0, mastery_level="critical"))
        session.add(MasteryState(student_id=student.id, concept_id=c_base.id, mastery_score=65.0, mastery_level="developing"))
        session.add(MasteryState(student_id=student.id, concept_id=c_rec.id, mastery_score=28.0, mastery_level="critical"))

        # Seed Evidence for Return Values
        session.add(DiagnosticEvidence(
            student_id=student.id,
            concept_id=c_ret.id,
            session_id=session_1.id,
            evidence_type="repeated_mistake",
            confidence_level="HIGH CONFIDENCE",
            explanation="Student repeatedly confused print() with return statements across 2 questions and teach-back."
        ))

        # Seed Recommendations targeting the Root Cause!
        session.add(Recommendation(
            student_id=student.id,
            target_concept_id=c_rec.id,
            root_cause_concept_id=c_ret.id,
            title="Prerequisite Bottleneck Detected: Return Values",
            reason="You attempted Recursion with 88% confidence but failed both questions. The root cause is NOT recursion syntax, but a foundational gap in Return Values (36% mastery).",
            action_steps=[
                "1. Study the difference between stdout (print) and returning values to the call stack.",
                "2. Understand why a recursive function requires `return func(n-1)` rather than just calling `func(n-1)`.",
                "3. Solve 2 return-value trace problems.",
                "4. Complete the Return Values Teach-Back."
            ],
            priority="high",
            is_completed=False
        ))

        await session.commit()
        print("Database seeding completed successfully with rich Python curriculum and demo evidence!")

if __name__ == "__main__":
    asyncio.run(seed_database())
