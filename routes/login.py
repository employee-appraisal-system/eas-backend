from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schema.login import LoginRequest
from services.login import authenticate_employee
from database.connection import get_db
import sqlalchemy.exc

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Login endpoint
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        employee = authenticate_employee(db, request.email, request.password)
        if not employee:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "message": "Login successful",
            "employee_id": employee.id,
            "role": employee.role,
        }

    except sqlalchemy.exc.SQLAlchemyError as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
