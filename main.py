from __future__ import annotations

import os
import socket
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, FastAPI, HTTPException, BackgroundTasks, Depends, Request
import uvicorn

from models.user import UserBase, UserRead, UserUpdate, UserRegistration
from utils.database import get_db
from utils.etag import create_etag_response

# Import export task functions
from services.export_tasks import run_export_task, run_export_all_task

import asyncio
import json

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

# -----------------------------------------------------------------------------
# User endpoints
    # User registration & login (JWT authentication)
    # Profile management (avatar, contact info, reputation)
    # Roles (tenant / landlord / admin)
    # You should have paths for each “resource” implementing GET, PUT, POST, DELETE. The methods can simply return NOT IMPLEMENTED.
# -----------------------------------------------------------------------------
users_router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@users_router.post("", status_code=201)
def create_user():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@users_router.get("")
def list_users(
        request: Request, 
        conn = Depends(get_db), 
        page: int = 1, 
        limit: int = 10, 
        role: str | None = None,
    ):
    cursor = conn.cursor(dictionary=True)
    offset = (page - 1) * limit

    try:
        # Count total items
        if role:
            cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role = %s", (role,))
        else:
            cursor.execute("SELECT COUNT(*) AS total FROM users")

        total = cursor.fetchone()["total"]

        # Fetch page
        if role:
            cursor.execute("""
                           SELECT * 
                           FROM users 
                           WHERE role = %s
                           ORDER BY id
                           LIMIT %s OFFSET %s
                           """, (role, limit, offset))
        else:
            cursor.execute("""
                           SELECT * 
                           FROM users 
                           ORDER BY id
                           LIMIT %s OFFSET %s
                           """, (limit, offset))
        
        users = cursor.fetchall()
        
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        
        # Add hypermedia links to each user
        base_url = str(request.base_url).rstrip("/")
        for user in users:
            user["_links"] = {
                "self": {"href": f"{base_url}/users/{user['id']}"},
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

@users_router.get("{user_id}")
def get_user(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@users_router.put("{user_id}")
def update_user(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@users_router.delete("{user_id}")
def delete_user(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@auth_router.post("register", status_code=201)
def register_user():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@auth_router.post("login")
def login():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@users_router.get("{user_id}/profile")
def get_profile(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@users_router.put("{user_id}/profile")
def update_profile(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@users_router.get("{user_id}/roles")
def get_roles(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@users_router.put("{user_id}/roles")
def update_roles(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

app.include_router(users_router)
app.include_router(auth_router)

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "User Service (endpoints not implemented yet)"}

# -----------------------------------------------------------------------------
# Export endpoints (if available)
# -----------------------------------------------------------------------------

# In-memory task tracking
export_tasks = {}

@app.post("/export/users/{role}", status_code=202)
async def export_users_by_role(role: str, background_tasks: BackgroundTasks):
    """Export users by role"""
    task_id = f"export_{role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    export_tasks[task_id] = {"status": "started", "role": role}
    background_tasks.add_task(run_export_task, task_id, role, export_tasks)
    return {"task_id": task_id}

@app.post("/export/users/", status_code=202)
async def export_all_users(background_tasks: BackgroundTasks):
    """Export all users"""
    task_id = f"export_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    export_tasks[task_id] = {"status": "started", "role": "all"}
    background_tasks.add_task(run_export_all_task, task_id, export_tasks)
    return {"task_id": task_id}

@app.get("/export/status/{task_id}")
async def get_export_status(task_id: str):
    """Get export status"""
    return export_tasks.get(task_id, {"error": "Task not found"})

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
