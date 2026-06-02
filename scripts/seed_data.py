"""
Seed script: adds real questions and creates two active appraisal cycles.
  Cycle A – "Mid-Year Review 2025"  → Self Assessment stage is active
  Cycle B – "Annual Appraisal 2025" → Lead Assessment stage is active

Run from the eas-backend directory:
    python scripts/seed_data.py
"""

import sys
import os
from datetime import date, timedelta

# Make sure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal
from models.questions import Question, Option
from models.appraisal_cycle import AppraisalCycle
from models.stages import Stage
from models.parameters import Parameter
from models.employee_allocation import EmployeeAllocation
from models.assignment import QuestionAssignment
from models.employee import Employee

# ─────────────────────────────────────────────
# QUESTIONS
# ─────────────────────────────────────────────
QUESTIONS = [
    # ---------- Descriptive ----------
    {
        "question_text": "Describe the key achievements you are most proud of during this appraisal period.",
        "question_type": "descriptive",
        "options": [],
    },
    {
        "question_text": "What were the main challenges you faced, and how did you overcome them?",
        "question_type": "descriptive",
        "options": [],
    },
    {
        "question_text": "What skills or competencies do you feel you need to develop further?",
        "question_type": "descriptive",
        "options": [],
    },
    {
        "question_text": "Describe a situation where you demonstrated strong teamwork or collaboration.",
        "question_type": "descriptive",
        "options": [],
    },
    {
        "question_text": "What are your career goals for the next 12 months, and how can the organisation support you?",
        "question_type": "descriptive",
        "options": [],
    },

    # ---------- Single Choice (rating scale) ----------
    {
        "question_text": "How would you rate your overall performance against the goals set at the beginning of this period?",
        "question_type": "single choice",
        "options": [
            "Outstanding – significantly exceeded all goals",
            "Exceeds Expectations – exceeded most goals",
            "Meets Expectations – achieved all goals",
            "Partially Meets Expectations – achieved some goals",
            "Does Not Meet Expectations – did not achieve goals",
        ],
    },
    {
        "question_text": "How effectively did you manage your time and prioritise tasks throughout this period?",
        "question_type": "single choice",
        "options": [
            "Very Effective – always delivered on time",
            "Effective – rarely missed deadlines",
            "Moderate – occasionally struggled with prioritisation",
            "Needs Improvement – frequently missed deadlines",
        ],
    },
    {
        "question_text": "How would you rate the quality of your work deliverables?",
        "question_type": "single choice",
        "options": [
            "Excellent – consistently high quality with minimal errors",
            "Good – mostly high quality, minor errors",
            "Satisfactory – acceptable quality, some rework needed",
            "Below Standard – frequent quality issues",
        ],
    },

    # ---------- MCQ (multiple select) ----------
    {
        "question_text": "Which of the following areas did you contribute to significantly this period? (Select all that apply)",
        "question_type": "mcq",
        "options": [
            "Product development",
            "Customer success",
            "Process improvement",
            "Team mentoring",
            "Cross-functional collaboration",
            "Innovation / new initiatives",
        ],
    },
    {
        "question_text": "Which training or learning activities did you complete during this period? (Select all that apply)",
        "question_type": "mcq",
        "options": [
            "Online certification or course",
            "Internal workshop or training",
            "Mentoring or coaching session",
            "Conference or industry event",
            "Self-directed reading / research",
            "None of the above",
        ],
    },

    # ---------- Yes/No ----------
    {
        "question_text": "Did you complete all mandatory compliance and safety training this period?",
        "question_type": "yes/no",
        "options": ["Yes", "No"],
    },
    {
        "question_text": "Were your performance goals clearly defined and communicated at the start of this period?",
        "question_type": "yes/no",
        "options": ["Yes", "No"],
    },
    {
        "question_text": "Have you received sufficient feedback from your manager to understand your performance?",
        "question_type": "yes/no",
        "options": ["Yes", "No"],
    },
]


def seed_questions(db):
    """Insert questions + options; skip if already present."""
    existing_texts = {q.question_text for q in db.query(Question.question_text).all()}
    added = []
    for q_data in QUESTIONS:
        if q_data["question_text"] in existing_texts:
            print(f"  [SKIP] Question already exists: {q_data['question_text'][:60]}…")
            continue
        q = Question(
            question_text=q_data["question_text"],
            question_type=q_data["question_type"],
        )
        db.add(q)
        db.flush()  # get question_id
        for opt_text in q_data["options"]:
            db.add(Option(question_id=q.question_id, option_text=opt_text))
        added.append(q)
        print(f"  [ADD] [{q_data['question_type'].upper():<14}] {q_data['question_text'][:70]}")
    db.flush()
    return added


def make_cycle(db, name, description, status, start, end, stages_config, parameters_config):
    """Create one appraisal cycle with stages & parameters."""
    cycle = AppraisalCycle(
        cycle_name=name,
        description=description,
        status=status,
        start_date_of_cycle=start,
        end_date_of_cycle=end,
    )
    db.add(cycle)
    db.flush()

    for sc in stages_config:
        stage = Stage(
            stage_name=sc["name"],
            cycle_id=cycle.cycle_id,
            start_date_of_stage=sc["start"],
            end_date_of_stage=sc["end"],
            is_active=sc.get("is_active", False),
            is_completed=sc.get("is_completed", False),
        )
        db.add(stage)

    for pc in parameters_config:
        param = Parameter(
            parameter_title=pc["title"],
            helptext=pc.get("helptext", ""),
            cycle_id=cycle.cycle_id,
            applicable_to_employee=pc.get("employee", True),
            applicable_to_lead=pc.get("lead", True),
            is_fixed_parameter=pc.get("fixed", False),
        )
        db.add(param)

    db.flush()
    print(f"  [CYCLE] Created '{name}' (id={cycle.cycle_id})")
    return cycle


def allocate_and_assign(db, cycle, employees, all_questions):
    """Allocate every employee to the cycle and assign all questions."""
    for emp in employees:
        # Check allocation
        existing_alloc = (
            db.query(EmployeeAllocation)
            .filter_by(cycle_id=cycle.cycle_id, employee_id=emp.id)
            .first()
        )
        if not existing_alloc:
            db.add(EmployeeAllocation(cycle_id=cycle.cycle_id, employee_id=emp.id))

        # Assign each question
        for q in all_questions:
            existing_assign = (
                db.query(QuestionAssignment)
                .filter_by(
                    employee_id=emp.id,
                    question_id=q.question_id,
                    cycle_id=cycle.cycle_id,
                )
                .first()
            )
            if not existing_assign:
                db.add(
                    QuestionAssignment(
                        employee_id=emp.id,
                        question_id=q.question_id,
                        cycle_id=cycle.cycle_id,
                    )
                )
    db.flush()
    print(f"    -> Allocated {len(employees)} employees, assigned {len(all_questions)} questions each")


def main():
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("  EAS SEED SCRIPT")
        print("=" * 60)

        # ── 1. Questions ──────────────────────────────────────────
        print("\n[1] Seeding questions...")
        seed_questions(db)

        # Fetch ALL questions (newly added + pre-existing)
        all_questions = db.query(Question).all()
        print(f"    Total questions in DB: {len(all_questions)}")

        # ── 2. Fetch all employees ────────────────────────────────
        employees = db.query(Employee).all()
        if not employees:
            print("\n[WARNING] No employees found in DB. Skipping allocation & assignment.")
        else:
            print(f"\n[2] Found {len(employees)} employees")

        # ── 3. Cycle A – Mid-Year Review 2025 ────────────────────
        #       Self Assessment stage is ACTIVE
        print("\n[3] Creating 'Mid-Year Review 2025' (Self Assessment active)...")
        today = date.today()

        # Cycle runs Jan – Jun 2025 (dates in the past/present for realism)
        c_start = date(2025, 1, 1)
        c_end   = date(2025, 12, 31)

        stages_a = [
            {"name": "Setup",            "start": date(2025, 1, 1),  "end": date(2025, 1, 31),  "is_active": False, "is_completed": True},
            {"name": "Self Assessment",  "start": date(2025, 2, 1),  "end": date(2025, 5, 31),  "is_active": True,  "is_completed": False},
            {"name": "Lead Assessment",  "start": date(2025, 6, 1),  "end": date(2025, 7, 31),  "is_active": False, "is_completed": False},
            {"name": "HR/VL Validation", "start": date(2025, 8, 1),  "end": date(2025, 9, 30),  "is_active": False, "is_completed": False},
            {"name": "Closure",          "start": date(2025, 10, 1), "end": date(2025, 12, 31), "is_active": False, "is_completed": False},
        ]

        params_common = [
            {"title": "Overall Performance Rating", "helptext": "Rate the employee's overall performance for this period.", "employee": True, "lead": True, "fixed": True},
            {"title": "Quality of Work",             "helptext": "Evaluate accuracy, thoroughness, and standard of output.", "employee": True, "lead": True, "fixed": False},
            {"title": "Communication Skills",        "helptext": "Assess written, verbal, and interpersonal communication.", "employee": True, "lead": True, "fixed": False},
            {"title": "Initiative & Innovation",     "helptext": "Recognise proactive contributions and creative thinking.", "employee": True, "lead": True, "fixed": False},
            {"title": "Teamwork & Collaboration",    "helptext": "Evaluate ability to work effectively with others.", "employee": True, "lead": True, "fixed": False},
        ]

        cycle_a = make_cycle(
            db,
            name="Mid-Year Review 2025",
            description="Mid-year performance review focusing on goal progress, self-reflection, and development planning for all employees.",
            status="active",
            start=c_start,
            end=c_end,
            stages_config=stages_a,
            parameters_config=params_common,
        )

        if employees:
            allocate_and_assign(db, cycle_a, employees, all_questions)

        # ── 4. Cycle B – Annual Appraisal 2025 ───────────────────
        #       Lead Assessment stage is ACTIVE
        print("\n[4] Creating 'Annual Appraisal 2025' (Lead Assessment active)...")

        stages_b = [
            {"name": "Setup",            "start": date(2024, 10, 1), "end": date(2024, 10, 31), "is_active": False, "is_completed": True},
            {"name": "Self Assessment",  "start": date(2024, 11, 1), "end": date(2024, 12, 31), "is_active": False, "is_completed": True},
            {"name": "Lead Assessment",  "start": date(2025, 1, 1),  "end": date(2025, 6, 30),  "is_active": True,  "is_completed": False},
            {"name": "HR/VL Validation", "start": date(2025, 7, 1),  "end": date(2025, 8, 31),  "is_active": False, "is_completed": False},
            {"name": "Closure",          "start": date(2025, 9, 1),  "end": date(2025, 9, 30),  "is_active": False, "is_completed": False},
        ]

        params_b = params_common + [
            {"title": "Technical Competency",   "helptext": "Assess depth of domain knowledge and technical skills.", "employee": True, "lead": True, "fixed": False},
            {"title": "Leadership & Ownership", "helptext": "Evaluate accountability, decision-making, and leadership.", "employee": False, "lead": True, "fixed": False},
        ]

        cycle_b = make_cycle(
            db,
            name="Annual Appraisal 2025",
            description="Comprehensive year-end performance appraisal covering all competency areas, career development, and goal-setting for the next year.",
            status="active",
            start=date(2024, 10, 1),
            end=date(2025, 9, 30),
            stages_config=stages_b,
            parameters_config=params_b,
        )

        if employees:
            allocate_and_assign(db, cycle_b, employees, all_questions)

        # ── 5. Commit ─────────────────────────────────────────────
        db.commit()
        print("\n" + "=" * 60)
        print("  * Seed complete!")
        print(f"  * {len(QUESTIONS)} question definitions processed")
        print(f"  * 2 cycles created (IDs: {cycle_a.cycle_id}, {cycle_b.cycle_id})")
        if employees:
            print(f"  * {len(employees)} employees allocated to each cycle")
        print("=" * 60 + "\n")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seed failed – rolling back.\n  {type(e).__name__}: {e}\n")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
