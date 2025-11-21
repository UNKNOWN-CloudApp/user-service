from __future__ import annotations

import os
import socket
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, BackgroundTasks
import uvicorn

from models.user import UserBase, UserRead, UserUpdate, UserRegistration

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
@app.post("/users", status_code=201)
def create_user():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.get("/users")
def list_users():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.get("/users/{user_id}")
def get_user(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.put("/users/{user_id}")
def update_user(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.delete("/users/{user_id}")
def delete_user(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.post("/auth/register", status_code=201)
def register_user():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.post("/auth/login")
def login():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.get("/users/{user_id}/profile")
def get_profile(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.put("/users/{user_id}/profile")
def update_profile(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.get("/users/{user_id}/roles")
def get_roles(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.put("/users/{user_id}/roles")
def update_roles(user_id: UUID):
    raise HTTPException(status_code=501, detail="Not implemented yet")

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
