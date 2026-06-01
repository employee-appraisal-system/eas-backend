"""
role_mapping.py
---------------
Maps Microsoft Entra ID (Azure AD) directory roles to the EAS application
roles (HR, Lead, Employee).

Configuration is entirely driven by environment variables so the mapping can
be changed without touching code:

    # Comma-separated Entra ID role display names that map to each app role.
    # A user is matched against ALL roles they hold; the first match wins in
    # priority order: HR > Lead > Employee.
    ROLE_MAP_HR=Global Administrator,Company Administrator
    ROLE_MAP_LEAD=User Administrator
    ROLE_MAP_EMPLOYEE=Office Apps Administrator

    # If the user holds none of the mapped roles (or no roles at all) they are
    # assigned this default app role.
    ROLE_MAP_DEFAULT=Employee

For the Graph API lookup (used by non-SSO / password logins) the service
re-uses the existing AZURE_TENANT_ID / AZURE_CLIENT_ID / AZURE_CLIENT_SECRET
credentials to obtain an app-only token and call:
    GET /v1.0/users/{email}/memberOf?$select=displayName

Make sure your App Registration has the 'Directory.Read.All' application
permission granted in Entra ID for this to work.
"""

from __future__ import annotations

import os
import logging

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

logger = logging.getLogger(__name__)


def _parse_role_list(env_key: str) -> list[str]:
    """Return a normalised list of Entra role names from a comma-separated env var."""
    raw = os.getenv(env_key, "")
    return [r.strip() for r in raw.split(",") if r.strip()]


ROLE_PRIORITY: list[tuple[str, list[str]]] = [
    ("HR", _parse_role_list("ROLE_MAP_HR")),
    ("Lead", _parse_role_list("ROLE_MAP_LEAD")),
    ("Employee", _parse_role_list("ROLE_MAP_EMPLOYEE")),
]

DEFAULT_APP_ROLE: str = os.getenv("ROLE_MAP_DEFAULT", "Employee")


CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")


_raw_tenant = os.getenv("AZURE_TENANT_ID", "common")
GRAPH_TENANT_ID = os.getenv("AZURE_GRAPH_TENANT_ID") or (
    _raw_tenant if _raw_tenant.lower() != "common" else None
)

if not GRAPH_TENANT_ID:
    logger.warning(
        "AZURE_GRAPH_TENANT_ID is not set and AZURE_TENANT_ID is 'common'. "
        "Graph API role lookups will be skipped — all users will receive the "
        "default role (%s). Set AZURE_GRAPH_TENANT_ID to your real tenant GUID.",
        DEFAULT_APP_ROLE,
    )

GRAPH_TOKEN_URL = (
    f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token"
    if GRAPH_TENANT_ID
    else None
)
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def map_entra_roles_to_app_role(entra_role_names: list[str]) -> str:
    """
    Given a list of Entra ID role/group display names held by a user,
    return the highest-priority app role they qualify for.

    Falls back to DEFAULT_APP_ROLE when no mapping matches.
    """
    user_roles_lower = {r.strip().lower() for r in entra_role_names}

    for app_role, entra_names in ROLE_PRIORITY:
        for entra_name in entra_names:
            if entra_name.strip().lower() in user_roles_lower:
                logger.debug(
                    "Mapped Entra role '%s' → app role '%s'", entra_name, app_role
                )
                return app_role

    logger.debug(
        "No Entra role matched for %s; defaulting to '%s'",
        entra_role_names,
        DEFAULT_APP_ROLE,
    )
    return DEFAULT_APP_ROLE


def resolve_role_from_token_claims(claims: dict) -> str:
    """
    During an SSO login the Azure ID/access token may contain:
      - claims["roles"]  — app-role values assigned in the App Registration manifest
      - claims["wids"]   — well-known directory role template GUIDs

    We also receive the user's directory role *display names* if the Graph API
    is called.  For SSO we prefer to call the Graph API with the delegated
    access_token so we get real role names, but we can also fall back to the
    'roles' claim.

    This function extracts whatever role names are available from claims and
    maps them to an app role.

    NOTE: The 'roles' claim in an ID token contains the *value* strings defined
    in the App Registration manifest (e.g. "bbw.hr"), NOT the display names.
    If you use those values as Entra role names in ROLE_MAP_* vars, this works
    fine.  Alternatively, supply actual display names and rely on the Graph
    lookup path.
    """
    role_values: list[str] = claims.get("roles", []) or []
    return map_entra_roles_to_app_role(role_values)


def _get_graph_app_token() -> str:
    """Obtain a client-credentials token for the Microsoft Graph API."""
    if not GRAPH_TOKEN_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AZURE_GRAPH_TENANT_ID is not configured. "
                "Cannot perform Graph API role lookup."
            ),
        )
    try:
        resp = httpx.post(
            GRAPH_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "https://graph.microsoft.com/.default",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to obtain Graph API app token: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach Microsoft Graph to verify roles.",
        )


def get_entra_roles_for_user(email: str) -> list[str]:
    """
    Call Microsoft Graph to retrieve the directory roles (and group names)
    assigned to a user identified by their UPN / email address.

    Returns a list of display names, e.g. ["Global Administrator"].
    Returns an empty list if the Graph tenant is not configured or if the
    call fails non-fatally (user not found, network error, etc.).
    """
    if not GRAPH_TENANT_ID:
        logger.debug(
            "Graph tenant not configured; skipping role lookup for '%s'.", email
        )
        return []

    try:
        token = _get_graph_app_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1) Find the user by mail, otherMails, or UPN
        search_url = (
            f"{GRAPH_BASE_URL}/users?$filter=mail eq '{email}' or "
            f"otherMails/any(id:id eq '{email}') or userPrincipalName eq '{email}'"
            "&$count=true&$select=id"
        )
        search_headers = {**headers, "ConsistencyLevel": "eventual"}
        search_resp = httpx.get(search_url, headers=search_headers, timeout=10)
        search_resp.raise_for_status()
        search_data = search_resp.json()
        
        if not search_data.get("value"):
            logger.warning("Graph API: user '%s' not found in Entra ID.", email)
            return []
            
        user_id = search_data["value"][0]["id"]

        # 2) Get their group/role memberships using their actual object ID
        url = f"{GRAPH_BASE_URL}/users/{user_id}/memberOf"
        resp = httpx.get(url, headers=headers, timeout=10)

        # 404 won't normally happen now since we just verified the user ID, but keep the check
        if resp.status_code == 404:
            logger.warning("Graph API: user ID '%s' not found for memberOf.", user_id)
            return []

        resp.raise_for_status()
        members = resp.json().get("value", [])

        display_names = [
            m.get("displayName", "") for m in members if m.get("displayName")
        ]
        logger.debug("Graph API roles for %s: %s", email, display_names)
        return display_names

    except HTTPException:
        raise
    except Exception as exc:
        logger.warning(
            "Graph API lookup failed for '%s' (non-fatal, defaulting role): %s",
            email,
            exc,
        )
        return []


def resolve_role_for_email(email: str) -> str:
    """
    Resolve the EAS app role for a user identified by email by querying
    Entra ID via the Graph API.  Used for non-SSO (password) logins.
    """
    entra_roles = get_entra_roles_for_user(email)
    return map_entra_roles_to_app_role(entra_roles)
