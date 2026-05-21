from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dao.parameter import (
    get_all_parameters,
    get_parameter_by_id,
    add_parameter,
    get_parameter_id_by_name,
)
from schema.parameter import ParameterCreate
from fastapi import HTTPException, status


def fetch_all_parameters(db: Session):
    """Service function to get all parameters."""
    try:
        parameters = get_all_parameters(db)
        if not parameters:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No parameters found"
            )
        return parameters
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching parameters: {str(e)}",
        )


def fetch_parameter_by_id(db: Session, parameter_id: int):
    """Get a parameter by ID."""
    try:
        parameter = get_parameter_by_id(db, parameter_id)
        if not parameter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parameter with ID {parameter_id} not found",
            )
        return parameter
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching parameter: {str(error)}",
        )


def create_parameter(db: Session, parameter_data: ParameterCreate):
    """Create a parameter with validation."""
    try:
        if not parameter_data.parameter_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parameter title cannot be empty",
            )

        return add_parameter(db, parameter_data.dict())
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating parameter: {str(e)}",
        )


def get_parameter_id(db: Session, cycle_id: int, parameter_title: str):
    """Get parameter ID by name and cycle ID"""
    try:
        parameter = get_parameter_id_by_name(db, cycle_id, parameter_title)
        if not parameter:
            return None
        return parameter[0]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching parameter ID: {str(e)}",
        )
