from __future__ import annotations

import os
import socket
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Path, Query
import uvicorn

from models.user import UserBase, UserRead, UserUpdate, UserRegistration

port = int(os.environ.get("FASTAPIPORT", 8000))

app = FastAPI(
    title="Booking Service",
    description="Booking microservice (stubbed endpoints).",
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
    return {"message": "Booking Service (endpoints not implemented yet)"}

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
