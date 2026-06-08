from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.login import authenticate_employee
from services.jwt_handler import create_access_token
from services.role_mapping import resolve_role_for_email

router = APIRouter(prefix="/auth/login", tags=["Login"])


@router.post("/")
def login(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")

    employee = authenticate_employee(db, email, password)

    if not employee:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # -----------------------------------------------------------------
    # Resolve the app role from Entra ID — do NOT trust the DB role.
    # We look up the user's directory roles in Entra ID by their email
    # and map them through the ROLE_MAP_* environment variables.
    # If the Graph API is unreachable or the user has no matching role,
    # the default role (ROLE_MAP_DEFAULT, typically "Employee") is used.
    # -----------------------------------------------------------------
    app_role = resolve_role_for_email(employee.email)

    access_token = create_access_token(
        {"employee_id": employee.id, "email": employee.email, "role": app_role}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "employee": {
            "employee_id": employee.id,
            "employee_name": employee.first_name,
            "role": app_role,
        },
    }
