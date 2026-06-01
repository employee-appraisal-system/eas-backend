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
from services.role_mapping import (
    get_entra_roles_for_user,
    map_entra_roles_to_app_role,
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

    The user's app role (HR / Lead / Employee) is determined by querying
    Entra ID via the Graph API for their directory roles and mapping those
    roles through the ROLE_MAP_* environment variables.  The role stored in
    the local database is intentionally NOT used.

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

    # Look up employee record in the local DB (for id / name only).
    employee = get_employee_by_azure_email(db, email)

    # -----------------------------------------------------------------
    # Resolve the app role from Entra ID — do NOT trust the DB role.
    # We call the Graph API with app credentials so we always get the
    # live directory role assignments for this user.
    # -----------------------------------------------------------------
    entra_roles = get_entra_roles_for_user(email)
    app_role = map_entra_roles_to_app_role(entra_roles)

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
        "email": employee.email,
    }
