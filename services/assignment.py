from sqlalchemy.orm import Session
from models.assignment import QuestionAssignment
from dao.employee_allocation import assign_employee_to_cycle
from schema.assignment import AssignmentCreate, AssignmentResponse
from collections import defaultdict
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status


# To assign the employees for the cycles
def create_question_assignment(db: Session, assignment_data: AssignmentCreate):
    try:
        new_assignments = []

        for employee_id in assignment_data.employee_ids:
            assign_employee_to_cycle(db, employee_id, assignment_data.cycle_id)

            for question_id in assignment_data.question_ids:
                new_assignments.append(
                    QuestionAssignment(
                        employee_id=employee_id,
                        cycle_id=assignment_data.cycle_id,
                        question_id=question_id,
                    )
                )

        db.add_all(new_assignments)
        db.commit()
        return [
            AssignmentResponse(
                employee_id=employee_id,
                cycle_id=assignment_data.cycle_id,
                question_ids=assignment_data.question_ids,
            )
            for employee_id in assignment_data.employee_ids
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error."
        )


def fetch_employee_assignments(db: Session, employee_id: int):
    """
    Retrieve all assignments for an employee, grouping questions by cycle.
    """
    try:
        assignments = (
            db.query(QuestionAssignment)
            .filter(QuestionAssignment.employee_id == employee_id)
            .all()
        )

        grouped_assignments = defaultdict(
            lambda: {"employee_id": employee_id, "cycle_id": None, "question_ids": []}
        )

        for assignment in assignments:
            grouped_assignments[assignment.cycle_id]["cycle_id"] = assignment.cycle_id
            grouped_assignments[assignment.cycle_id]["question_ids"].append(
                assignment.question_id
            )

        return [AssignmentResponse(**data) for data in grouped_assignments.values()]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def fetch_assigned_questions(db: Session, employee_id: int, cycle_id: int):
    """
    Fetch questions assigned to an employee for a specific appraisal cycle.
    """
    try:
        assignments = (
            db.query(QuestionAssignment)
            .filter(
                QuestionAssignment.employee_id == employee_id,
                QuestionAssignment.cycle_id == cycle_id,
            )
            .all()
        )

        question_ids = [assignment.question_id for assignment in assignments]

        return AssignmentResponse(
            employee_id=employee_id, cycle_id=cycle_id, question_ids=question_ids
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
