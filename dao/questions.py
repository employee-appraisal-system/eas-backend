from sqlalchemy.orm import Session, selectinload
from models.questions import Question, Option
from schema.questions import QuestionSchema
from typing import List
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from logger_config import logging


def get_all_questions(db: Session) -> List[Question]:
    """
    Fetch all questions from the database

    Args:
        db: Database session

    Returns:
        List of questions with their IDs and texts

    Raises:
        SQLAlchemyError: If there's a database-related error
    """
    try:
        return db.query(Question.question_id, Question.question_text).all()
    except SQLAlchemyError as e:
        logging.error(f"Error fetching all questions: {str(e)}")
        raise


def get_all_questions_with_option(db: Session) -> List[Question]:
    """
    Fetch all questions with their options from the database

    Args:
        db: Database session

    Returns:
        List of questions with their options

    Raises:
        SQLAlchemyError: If there's a database-related error
    """
    try:
        return db.query(Question).options(selectinload(Question.options)).all()
    except SQLAlchemyError as e:
        logging.error(f"Error fetching questions with options: {str(e)}")
        raise


def add_new_question(question_data: QuestionSchema, db: Session) -> Question:
    """
    Add a new question to the database

    Args:
        question_data: Question data containing type and text
        db: Database session

    Returns:
        Newly created question object

    Raises:
        IntegrityError: If there's a constraint violation
        SQLAlchemyError: If there's another database-related error
    """
    try:
        new_question = Question(
            question_type=question_data.question_type,
            question_text=question_data.question_text,
        )
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        return new_question
    except IntegrityError as e:
        db.rollback()
        logging.error(f"Integrity error adding new question: {str(e)}")
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error adding new question: {str(e)}")
        raise


def add_options(question_id: int, options: List[str], db: Session) -> List[Option]:
    """
    Add options for MCQ, Single Choice, or Yes/No questions

    Args:
        question_id: ID of the question to add options for
        options: List of option text strings
        db: Database session

    Returns:
        List of created option objects

    Raises:
        IntegrityError: If there's a constraint violation
        SQLAlchemyError: If there's another database-related error
    """
    try:
        option_objects = [
            Option(question_id=question_id, option_text=opt.option_text)
            for opt in options
        ]
        db.add_all(option_objects)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logging.error(
            f"Integrity error adding options for question {question_id}: {str(e)}"
        )
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error adding options for question {question_id}: {str(e)}")
        raise
