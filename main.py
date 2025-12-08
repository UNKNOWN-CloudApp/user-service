from __future__ import annotations

import os
from fastapi import APIRouter, FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models.user import UserBase, UserRead, UserUpdate, UserRegistration
from utils.database import get_db
from utils.etag import create_etag_response



port_env = os.environ.get("PORT") or os.environ.get("FASTAPIPORT") or "8000"
try:
    port = int(port_env)
except ValueError:
    port = 8000

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
# User endpoints
    # User registration & login (JWT authentication)
    # Profile management
    # You should have paths for each “resource” implementing GET, PUT, POST, DELETE. 
# -----------------------------------------------------------------------------
users_router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@users_router.post("", status_code=201)
def create_user(
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        token: str = None,
        conn = Depends(get_db),
):
    cursor = conn.cursor(dictionary=True)

    # Check if email already used
    cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Check if token already used
    cursor.execute("SELECT email FROM users WHERE token=%s", (token,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Token is already used")
    
    cursor.execute(
        """
        INSERT INTO users (email, first_name, last_name, token)
        VALUES (%s, %s, %s, %s)
        """,
        (email, first_name, last_name, token)
    )

    # Commit the transaction
    conn.commit()

    cursor.close()

    return {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "token": token
    }

@users_router.get("", status_code=200)
def list_users(
        request: Request, 
        conn = Depends(get_db), 
        page: int = 1, 
        limit: int = 10,
    ):
    cursor = conn.cursor(dictionary=True)
    offset = (page - 1) * limit

    try:
        # Count total items
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total = cursor.fetchone()["total"]

        # Fetch page
        cursor.execute("""
                       SELECT * 
                       FROM users 
                       ORDER BY email
                       LIMIT %s OFFSET %s
                       """, (limit, offset))
        
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
            "pages": (total // limit) + int(total % limit > 0)
        }
        
        return create_etag_response(request, response_body)

    finally:
        cursor.close()

@users_router.get("/{token}", status_code=200)
def get_user(token: str, request: Request, conn = Depends(get_db)):
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
        first_name: str | None = None,
        last_name: str | None = None,
        conn = Depends(get_db)
):
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
def delete_user(token: str, conn = Depends(get_db)):
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

@auth_router.post("register", status_code=201)
def register_user():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@auth_router.post("login", status_code=200)
def login():
    raise HTTPException(status_code=501, detail="Not implemented yet")

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
