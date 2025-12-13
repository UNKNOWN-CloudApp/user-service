"""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
FastAPI demo showing Google OIDC login -> app-issued JWT -> protected microservice.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# import jwt
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from pydantic import BaseModel

# Auth / JWT Libraries
from jose import JWTError, jwt
from google.oauth2 import id_token

from models.user import UserBase, UserRead, UserRegistration, UserUpdate
from utils.database import get_db
from utils.etag import create_etag_response



# -----------------------------------------------------------------------------
# Basic settings
# -----------------------------------------------------------------------------
port_env = os.environ.get("PORT") or os.environ.get("FASTAPIPORT") or "8080"
try:
    port = int(port_env)
except ValueError:
    port = 8080

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "1038095584126-tckmgh956ai8220d9atiualu8j8p2iri.apps.googleusercontent.com",
)
APP_JWT_SECRET = os.environ.get("APP_JWT_SECRET", "dev-secret-change-me")
APP_JWT_ALGORITHM = os.environ.get("APP_JWT_ALGORITHM", "HS256")
APP_JWT_ALG = "HS256"
APP_JWT_AUD = "user-service-audience"
APP_JWT_EXPIRE_MINUTES = int(os.environ.get("APP_JWT_EXPIRE_MINUTES", "60"))
APP_JWT_EXPIRES_MIN = int(os.getenv("APP_JWT_EXPIRES_MIN", "60"))

bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI(
    title="User Service",
    description="User microservice (stubbed endpoints).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------
class GoogleLoginRequest(BaseModel):
    id_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


# -----------------------------------------------------------------------------
# Auth helpers
# -----------------------------------------------------------------------------
def create_access_token(claims: Dict[str, Any]) -> str:
    expires_at = datetime.utcnow() + timedelta(minutes=APP_JWT_EXPIRE_MINUTES)
    payload = {**claims, "exp": expires_at}
    return jwt.encode(payload, APP_JWT_SECRET, algorithm=APP_JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = credentials.credentials
    try:
        return jwt.decode(
            token,
            APP_JWT_SECRET,
            algorithms=[APP_JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# -----------------------------------------------------------------------------
# Auth Helper Classes & Functions
# -----------------------------------------------------------------------------

class GoogleToken(BaseModel):
    """Accept either `id_token` or Google `credential` field."""
    id_token: Optional[str] = None
    credential: Optional[str] = None

    def get_token(self) -> str:
        return self.id_token or self.credential or ""

def _encode_app_jwt(claims: Dict[str, Any]) -> str:
    """Generates the internal API JWT used for service-to-service or frontend auth."""
    expires = datetime.utcnow() + timedelta(minutes=APP_JWT_EXPIRES_MIN)
    payload = {**claims, "exp": expires, "aud": APP_JWT_AUD}
    return jwt.encode(payload, APP_JWT_SECRET, algorithm=APP_JWT_ALG)

def _verify_app_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """Dependency to protect endpoints using the internal App JWT."""
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    token = credentials.credentials
    try:
        return jwt.decode(
            token,
            APP_JWT_SECRET,
            algorithms=[APP_JWT_ALG],
            audience=APP_JWT_AUD,
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid app token: {exc}",
        ) from exc



# -----------------------------------------------------------------------------
# Routers
# -----------------------------------------------------------------------------
users_router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# -----------------------------------------------------------------------------
# Auth Endpoints (Google Login)
# -----------------------------------------------------------------------------
@app.get("/api/profile")
def read_profile(claims: Dict[str, Any] = Depends(_verify_app_jwt)) -> Dict[str, Any]:
    """Protected microservice endpoint that requires the app-issued JWT."""
    return {
        "message": "You are authorized to view this profile.",
        
    }


@auth_router.post("/google", status_code=200)
def exchange_google_token(
    payload: GoogleToken = Body(...),
    conn = Depends(get_db)
):
    """
    1. Verifies Google Token.
    2. Checks DB for existing user by email.
    3. If user missing, creates one automatically (JIT Provisioning).
    4. Returns App JWT.
    """
    # 1. Verify Google Token
    google_token = payload.get_token()
    if not google_token:
        raise HTTPException(status_code=422, detail="Missing id_token/credential.")
    
    try:
        google_claims = id_token.verify_oauth2_token(
            google_token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {exc}")

    google_sub = google_claims.get("sub")
    if not google_sub:
        raise HTTPException(status_code=400, detail="Google token missing subject.")
    email = google_claims.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google token missing email scope.")

    # 2. Interact with Database
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        user_token_id = google_sub

        if existing_user:
            # User exists, grab their internal ID/Token
            if existing_user["token"] != google_sub:
                cursor.execute(
                    "UPDATE users SET token = %s WHERE email = %s",
                    (google_sub, email),
                )
                conn.commit()
            
            # Optional: Update profile picture or name from Google if changed?
            # For now, we just proceed to login.
        else:
            # 3. Register new user
            first_name = google_claims.get("given_name") or google_claims.get("name", "User")
            last_name = google_claims.get("family_name", "")
            
            cursor.execute(
                """
                INSERT INTO users (email, first_name, last_name, token)
                VALUES (%s, %s, %s, %s)
                """,
                (email, first_name, last_name, user_token_id)
            )
            conn.commit()

        # 4. Generate App JWT
        app_claims = {
            "sub": user_token_id,  # Subject is now our DB token/ID
            "email": email,
            "iss": "user-service",
            "name": google_claims.get("name"),
            "picture": google_claims.get("picture"),
        }
        jwt_token = _encode_app_jwt(app_claims)

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user_info": {
                "token": user_token_id,
                "email": email,
                "first_name": google_claims.get("given_name"),
            }
        }
    finally:
        cursor.close()

# @auth_router.post("/google", response_model=AccessTokenResponse, status_code=200)
# def login_with_google(payload: GoogleLoginRequest):
#     if not GOOGLE_CLIENT_ID:
#         raise HTTPException(
#             status_code=500,
#             detail="GOOGLE_CLIENT_ID is not configured on the server",
#         )

#     try:
#         idinfo = google_id_token.verify_oauth2_token(
#             payload.id_token,
#             google_requests.Request(),
#             GOOGLE_CLIENT_ID,
#         )
#     except ValueError as exc:
#         raise HTTPException(status_code=401, detail="Invalid Google ID token") from exc

#     user_claims = {
#         "sub": idinfo.get("sub"),
#         "email": idinfo.get("email"),
#         "name": idinfo.get("name"),
#         "picture": idinfo.get("picture"),
#         "iss": "user-service",
#     }

#     access_token = create_access_token(user_claims)
#     return AccessTokenResponse(
#         access_token=access_token,
#         expires_in=APP_JWT_EXPIRE_MINUTES * 60,
#         user=user_claims,
#     )


@auth_router.post("/register", status_code=501)
def register_user():
    raise HTTPException(status_code=501, detail="Not implemented yet")


@auth_router.post("/login", status_code=501)
def login():
    raise HTTPException(status_code=501, detail="Not implemented yet")


@users_router.get("/me", status_code=200)
def read_current_user(current_user=Depends(get_current_user)):
    return {
        "message": "Authenticated request to user microservice succeeded",
        "token_claims": current_user,
    }


@users_router.post("", status_code=201)
def create_user(
    email: str,
    first_name: str | None = None,
    last_name: str | None = None,
    token: str | None = None,
    conn=Depends(get_db),
):
    cursor = conn.cursor(dictionary=True)

    # Check if email already used
    cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )

    # Check if token already used
    cursor.execute("SELECT email FROM users WHERE token=%s", (token,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Token is already used")

    cursor.execute(
        """
        INSERT INTO users (email, first_name, last_name, token)
        VALUES (%s, %s, %s, %s)
        """,
        (email, first_name, last_name, token),
    )

    # Commit the transaction
    conn.commit()

    cursor.close()

    return {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "token": token,
    }


@users_router.get("", status_code=200)
def list_users(
    request: Request,
    conn=Depends(get_db),
    page: int = 1,
    limit: int = 10,
    current_user=Depends(get_current_user),
):
    cursor = conn.cursor(dictionary=True)
    offset = (page - 1) * limit

    try:
        # Count total items
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total = cursor.fetchone()["total"]

        # Fetch page
        cursor.execute(
            """
                       SELECT * 
                       FROM users 
                       ORDER BY email
                       LIMIT %s OFFSET %s
                       """,
            (limit, offset),
        )

        users = cursor.fetchall()

        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        # Add hypermedia links to each user
        base_url = str(request.base_url).rstrip("/")
        for user in users:
            user["_links"] = {
                "self": {"href": f"{base_url}/users/{user['token']}"},
            }

        response_body = {
            "users": users,
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total // limit) + int(total % limit > 0),
        }

        return create_etag_response(request, response_body)

    finally:
        cursor.close()

@users_router.get("/exists", status_code=200)
def user_exists(email: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT 1 FROM users WHERE email=%s LIMIT 1", (email,))
        return {"exists": cursor.fetchone() is not None}
    finally:
        cursor.close()

@users_router.get("/{token}", status_code=200)
def get_user(
    token: str,
    request: Request,
    claims: Dict[str, Any] = Depends(_verify_app_jwt),
    conn=Depends(get_db),
):
    if claims.get("sub") != token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not match the authenticated user",
        )
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE token = %s", (token,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return create_etag_response(request, user)

    finally:
        cursor.close()

@users_router.put("/{token}", status_code=200)
def update_user(
    token: str,
    request: Request,
    claims: Dict[str, Any] = Depends(_verify_app_jwt),
    first_name: str | None = None,
    last_name: str | None = None,
    conn=Depends(get_db),
):
    if claims.get("sub") != token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not match the authenticated user",
        )
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE token = %s", (token,))
        existing_user = cursor.fetchone()

        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []

        if first_name is not None:
            update_fields.append("first_name = %s")
            update_values.append(first_name)

        if last_name is not None:
            update_fields.append("last_name = %s")
            update_values.append(last_name)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Add token for WHERE clause
        update_values.append(token)

        update_query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE token = %s
        """

        cursor.execute(update_query, update_values)
        conn.commit()

        # Fetch updated user
        cursor.execute("SELECT * FROM users WHERE token = %s", (token,))
        updated_user = cursor.fetchone()

        return create_etag_response(request, updated_user)

    finally:
        cursor.close()


@users_router.delete("/{token}", status_code=204)
def delete_user(token: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE token = %s", (token,))
        existing_user = cursor.fetchone()

        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Delete the user
        cursor.execute("DELETE FROM users WHERE token = %s", (token,))
        conn.commit()

        # Return empty response for 204 No Content
        return None

    finally:
        cursor.close()


app.include_router(users_router)
app.include_router(auth_router)


# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/", status_code=200)
def root():
    return {"message": "User Service"}


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
