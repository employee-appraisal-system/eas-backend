from sqlalchemy.orm import Session
from dao.employee import get_employee_by_email
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from services.password_utils import verify_password


def authenticate_employee(db: Session, email: str, password: str):

    try:
        employee = get_employee_by_email(db, email)
        

        if not employee:
            return None

        if not verify_password(password, employee.password):
            return None

        return employee

    except SQLAlchemyError as exception:
        print(f"Database error occurred: {exception}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )

    except Exception as e:
        print(f"Unexpected error: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )