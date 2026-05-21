from sqlalchemy.orm import Session
from models.assignment import QuestionAssignment
from models.questions import Question
from models.employee import Employee
from models.appraisal_cycle import AppraisalCycle
from schema.assignment import AssignmentCreate, AssignmentResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional


def assign_questions_to_employee(
    db: Session, employee_id: int, question_ids: List[int], cycle_id: int
) -> List[QuestionAssignment]:
    """
    Assign questions to an employee for a specific cycle

    Args:
        db: Database session
        employee_id: ID of the employee
        question_ids: List of question IDs to assign
        cycle_id: ID of the appraisal cycle

    Returns:
        List of created assignments

    Raises:
        SQLAlchemyError: For database-related errors
    """
    try:
        # Fetch existing assignments to prevent duplicate entries
        existing_assignments = (
            db.query(QuestionAssignment.question_id)
            .filter(
                QuestionAssignment.employee_id == employee_id,
                QuestionAssignment.cycle_id == cycle_id,
                QuestionAssignment.question_id.in_(question_ids),
            )
            .all()
        )

        # Extract already assigned question IDs
        assigned_question_ids = {q_id for (q_id,) in existing_assignments}

        # Filter out questions that are already assigned
        new_question_ids = [
            q_id for q_id in question_ids if q_id not in assigned_question_ids
        ]

        if not new_question_ids:
            return []

        # Prepare and insert new assignments
        assignments = [
            QuestionAssignment(
                employee_id=employee_id, question_id=q_id, cycle_id=cycle_id
            )
            for q_id in new_question_ids
        ]

        # Add and commit assignments
        db.add_all(assignments)
        db.commit()
        return assignments
    except SQLAlchemyError as db_err:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise


def get_assignment_by_employee(
    db: Session, employee_id: int
) -> List[QuestionAssignment]:
    """
    Retrieve all assignments for a specific employee

    Args:
        db: Database session
        employee_id: ID of the employee

    Returns:
        List of assignments

    Raises:
        SQLAlchemyError: For database-related errors
    """
    try:
        # Fetch assignments
        assignments = (
            db.query(QuestionAssignment)
            .filter(QuestionAssignment.employee_id == employee_id)
            .all()
        )
        return assignments
    except SQLAlchemyError as db_err:
        raise
    except Exception as e:
        raise


def get_assigned_questions(
    db: Session, employee_id: int, cycle_id: int
) -> List[Question]:
    """
    Retrives questions assigned to an employee for a specific cycle

    Args:
        db: Database session
        employee_id: ID of the employee
        cycle_id: ID of the appraisal cycle

    Returns:
        List of assigned questions

    Raises:
        SQLAlchemyError: For database-related errors
    """
    try:
        assigned_questions = (
            db.query(Question)
            .join(QuestionAssignment)
            .filter(
                QuestionAssignment.employee_id == employee_id,
                QuestionAssignment.cycle_id == cycle_id,
            )
            .all()
        )
        return assigned_questions
    except SQLAlchemyError as db_err:
        raise
    except Exception as e:
        raise
