import os, httpx
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.employee import Employee

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("AZURE_REDIRECT_URI")
SCOPE = os.getenv("AZURE_SCOPE", "openid profile email User.Read")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
JWKS_URI = f"{AUTHORITY}/discovery/v2.0/keys"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"
AUTHORIZE_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"


def get_login_url():
    """Build the Microsoft OAuth2 authorization URL."""
    scope_encoded = SCOPE.replace(" ", "%20")
    url = (
        f"{AUTHORIZE_URL}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_mode=query"
        f"&scope={scope_encoded}"
        f"&state=random_state_string"
    )
    return url


def exchange_code_for_token(code):
    """Exchange the authorization code for tokens from Microsoft."""
    try:
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
            "scope": SCOPE,
        }
        response = httpx.post(TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Azure token exchange failed: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code for token: {str(e)}",
        )


def get_azure_public_keys():
    """Fetch Microsoft's public signing keys."""
    try:
        response = httpx.get(JWKS_URI)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Azure public keys: {str(e)}",
        )


def validate_id_token(id_token):
    """Validate the Azure ID token and return its claims."""
    try:
        jwks = get_azure_public_keys()
        unverified_header = jwt.get_unverified_header(id_token)

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find matching public key",
            )

        payload = jwt.decode(
            id_token,
            rsa_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
        )
        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
        )


def extract_email_from_claims(claims):
    """Extract the user's email/UPN from token claims."""
    email = (
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("upn")
        or claims.get("unique_name")
    )
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract email from Azure token",
        )
    return email


def get_employee_by_azure_email(db: Session, email):
    print("MICROSOFT LOGIN EMAIL:", email)
    """Look up employee in DB by matching Azure email against role_id column."""
    try:
        employee = db.query(Employee).filter(Employee.email == email).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No employee found with email: {email}. Contact your administrator.",
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while looking up employee: {str(e)}",
        )
