from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from services.jwt_handler import create_access_token
from services.azure_auth import (
    get_login_url,
    exchange_code_for_token,
    validate_id_token,
    extract_email_from_claims,
    get_employee_by_azure_email,
)

router = APIRouter(prefix="/auth", tags=["SSO"])


@router.get("/sso/login")
def sso_login():
    """Return the Microsoft login URL for the frontend to redirect to."""
    login_url = get_login_url()
    return {"login_url": login_url}


@router.post("/sso/callback")
def sso_callback(payload: dict, db: Session = Depends(get_db)):
    """
    Accepts the authorization code from Microsoft (sent by frontend),
    exchanges it for tokens, validates, and returns employee info.

    Expected body: { "code": "...", "state": "..." }
    """
    code = payload.get("code")
    if not code:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Authorization code is missing")

    token_response = exchange_code_for_token(code)

    id_token = token_response.get("id_token")
    if not id_token:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="ID token not received from Azure")

    claims = validate_id_token(id_token)

    email = extract_email_from_claims(claims)

    employee = get_employee_by_azure_email(db, email)

    access_token = create_access_token(
        {"employee_id": employee.id, "email": employee.email, "role": employee.role}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "employee_id": employee.id,
        "role": employee.role,
        "employee_name": employee.first_name,
        "email": employee.email,
    }
