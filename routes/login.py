from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.login import authenticate_employee
from services.jwt_handler import create_access_token

router = APIRouter(prefix="/auth/login", tags=["Login"])


@router.post("/")
def login(payload: dict, db: Session = Depends(get_db)):

    email = payload.get("email")
    password = payload.get("password")

    employee = authenticate_employee(db, email, password)

    if not employee:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        {"employee_id": employee.id, "email": employee.email, "role": employee.role}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "employee": {
            "employee_id": employee.id,
            "employee_name": employee.first_name,
            "role": employee.role,
        },
    }
