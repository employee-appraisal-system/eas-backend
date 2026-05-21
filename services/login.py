from sqlalchemy.orm import Session
from dao.employee import get_employee_by_email
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status


def authenticate_employee(db: Session, email: str, password: str):
    """Authenticate employee by checking if the provided password matches the stored one."""
    try:
        # To fetch the employee based on role ID
        employee = get_employee_by_email(db, email)

        # For no employee found
        if not employee:
            return None

        # For password mismatch
        if employee.password != password:
            return None

        # For successful authentication
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
