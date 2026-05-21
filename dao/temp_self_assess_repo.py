from sqlalchemy.orm import Session
from sqlalchemy import select, func, literal
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError, DataError
from models.self_assessment_response import SelfAssessmentResponse
from models.questions import Question
from models.employee import Employee
from models.employee_allocation import EmployeeAllocation
from typing import List, Dict
from logger_config import logging


def get_response(db: Session, cycle_id: int) -> List[Dict[str, str]]:
    """
    Retrieve self-assessment responses for a specific cycle

    Args:
        db: Database session
        cycle_id: ID of the appraisal cycle

    Returns:
        List of dictionaries containing self-assessment responses

    Raises:
        ValueError: For invalid input parameters
        SQLAlchemyError: For database-related errors
    """
    try:
        # Validate input
        if not isinstance(cycle_id, int) or cycle_id <= 0:
            logging.warning(f"Invalid cycle_id provided: {cycle_id}")
            raise ValueError(
                f"Invalid cycle_id: {cycle_id}. Must be a positive integer."
            )

        # Create alias for Question to avoid ambiguity
        QuestionAlias = aliased(Question)

        # Subquery to get distinct questions for the cycle
        subquery_questions = (
            db.query(SelfAssessmentResponse.question_id)
            .filter(SelfAssessmentResponse.cycle_id == cycle_id)
            .distinct()
            .subquery()
        )

        # Cross join to get all employee-question combinations for the cycle
        cross_joined = (
            db.query(EmployeeAllocation.employee_id, subquery_questions.c.question_id)
            .filter(EmployeeAllocation.cycle_id == cycle_id)
            .join(Employee, Employee.id == EmployeeAllocation.employee_id)
            .join(subquery_questions, literal(True))  # cross join
            .subquery()
        )

        # Main query to fetch responses
        result = (
            db.query(
                Employee.id,
                Employee.full_name,
                Question.question_text,
                func.coalesce(SelfAssessmentResponse.response_text, literal("-")).label(
                    "response_text"
                ),
            )
            .select_from(cross_joined)
            .join(Employee, Employee.id == cross_joined.c.employee_id)
            .join(Question, Question.question_id == cross_joined.c.question_id)
            .outerjoin(
                SelfAssessmentResponse,
                (SelfAssessmentResponse.employee_id == cross_joined.c.employee_id)
                & (SelfAssessmentResponse.question_id == cross_joined.c.question_id)
                & (SelfAssessmentResponse.cycle_id == cycle_id),
            )
            .order_by(Employee.id, Question.question_id)
        )

        # Convert to list of dictionaries
        response = [
            {
                "employee_id": row.employee_id,
                "employee_name": row.employee_name,
                "question_text": row.question_text,
                "response_text": row.response_text,
            }
            for row in result.all()
        ]

        logging.info(
            f"Retrieved {len(response)} self-assessment responses for cycle {cycle_id}"
        )

        return response

    except ValueError as val_err:
        logging.error(f"Validation error in get_response: {str(val_err)}")
        raise

    except DataError as data_err:
        logging.error(
            f"Data error while retrieving responses for cycle {cycle_id}: {str(data_err)}"
        )
        raise SQLAlchemyError(f"Data processing error: {str(data_err)}")

    except SQLAlchemyError as db_err:
        logging.error(
            f"Database error retrieving responses for cycle {cycle_id}: {str(db_err)}"
        )
        raise

    except Exception as e:
        logging.error(
            f"Unexpected error retrieving responses for cycle {cycle_id}: {str(e)}"
        )
        raise
