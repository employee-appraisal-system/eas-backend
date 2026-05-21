from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models.parameters import Parameter
from typing import Optional, List, Tuple


def get_all_parameters(db: Session) -> List[Parameter]:
    """Fetch all parameters from the database."""
    try:
        return db.query(Parameter).all()
    except SQLAlchemyError as error:
        db.rollback()
        raise error


def get_parameter_by_id(db: Session, parameter_id: int) -> Optional[Parameter]:
    """Fetch a single parameter by ID."""
    try:
        return (
            db.query(Parameter).filter(Parameter.parameter_id == parameter_id).first()
        )
    except SQLAlchemyError as error:
        db.rollback()
        raise error


def add_parameter(db: Session, parameter_data: dict) -> Parameter:
    """Add a new parameter to the database."""
    try:
        new_parameter = Parameter(**parameter_data)
        db.add(new_parameter)
        db.commit()
        db.refresh(new_parameter)
        return new_parameter
    except IntegrityError as error:
        db.rollback()
        raise SQLAlchemyError(f"Integrity error: {str(error)}")
    except SQLAlchemyError as error:
        db.rollback()
        raise error


def get_parameters_for_cycle(
    db: Session, cycle_id: int, is_lead: bool
) -> List[Parameter]:
    """Fetch parameters for a given cycle based on employee role"""
    try:
        return (
            db.query(Parameter)
            .filter(
                Parameter.cycle_id == cycle_id,
                (
                    Parameter.applicable_to_lead
                    if is_lead
                    else Parameter.applicable_to_employee
                )
                == True,
            )
            .all()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_parameter_id_by_name(
    db: Session, cycle_id: int, parameter_title: str
) -> Optional[Tuple[int]]:
    try:
        return (
            db.query(Parameter.parameter_id)
            .filter(
                Parameter.cycle_id == cycle_id,
                Parameter.parameter_title == parameter_title,
            )
            .first()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e
