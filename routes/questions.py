from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from database.connection import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schema.questions import QuestionSchema, QuestionResponseSchema, QuestionsSchema
from typing import List
from dao.questions import (
    get_all_questions,
    add_new_question,
    add_options,
    get_all_questions_with_option,
)
import logging
from logger_config import logging

router = APIRouter(tags=["Questions"])


# Fetch all questions
@router.get("/question", response_model=List[QuestionsSchema])
def list_question(db: Session = Depends(get_db)):
    try:
        questions = get_all_questions(db)
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No questions found"
            )
        return questions
    except SQLAlchemyError as e:
        logging.error(f"Database error when fetching questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve questions from database",
        )
    except Exception as e:
        logging.error(f"Unexpected error in list_question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# Fetch all questions with options
@router.get("/questions-with-options", response_model=List[QuestionResponseSchema])
def list_of_questions_with_options(db: Session = Depends(get_db)):
    try:
        questions = get_all_questions_with_option(db)
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No questions found"
            )
        return questions
    except SQLAlchemyError as e:
        logging.error(f"Database error when fetching questions with options: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve questions with options from database",
        )
    except Exception as e:
        logging.error(f"Unexpected error in list_of_questions_with_options: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# Add a new question
@router.post(
    "/question",
    response_model=QuestionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def add_question(question_data: QuestionSchema, db: Session = Depends(get_db)):
    try:
        if not question_data.question_text or not question_data.question_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question text and type are required",
            )

        if question_data.question_type in ["MCQ", "Single Choice", "Yes/No"]:
            if not question_data.options or len(question_data.options) < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{question_data.question_type} questions require at least one option",
                )

        new_question = add_new_question(question_data, db)

        if (
            question_data.question_type in ["MCQ", "Single Choice", "Yes/No"]
            and question_data.options
        ):
            add_options(new_question.question_id, question_data.options, db)

        return JSONResponse(
            content={
                "message": "Question added successfully",
                "question_id": new_question.question_id,
            },
            status_code=status.HTTP_201_CREATED,
        )
    except IntegrityError as e:
        db.rollback()
        logging.error(f"Database integrity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Question could not be added due to a conflict with existing data",
        )
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Database error when adding question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add question to database",
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Unexpected error in add_question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
