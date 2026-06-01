from __future__ import annotations

import re
from typing import Iterable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.jwt_handler import verify_access_token

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    payload = verify_access_token(token)
    return payload


_ROLE_NORMALIZE_RE = re.compile(r"[\s_-]+")


def normalize_role(role: str | None) -> str:
    if not role:
        return ""
    return _ROLE_NORMALIZE_RE.sub("", str(role).strip().lower())


def require_roles(*allowed_roles: str):
    allowed = {normalize_role(r) for r in allowed_roles if r}

    def _dependency(user: dict = Depends(get_current_user)) -> dict:
        user_role = normalize_role(user.get("role"))
        if user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return user

    return _dependency


def require_self_or_roles(param_name: str, *privileged_roles: str):
    privileged = {normalize_role(r) for r in privileged_roles if r}

    def _dependency(request: Request, user: dict = Depends(get_current_user)) -> dict:
        user_role = normalize_role(user.get("role"))
        if user_role in privileged:
            return user

        requested_id = request.path_params.get(param_name)
        token_employee_id = user.get("employee_id")

        if requested_id is None or token_employee_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request",
            )

        if str(token_employee_id) != str(requested_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return user

    return _dependency
