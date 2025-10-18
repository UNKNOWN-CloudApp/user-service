from __future__ import annotations

from typing import Optional, Literal
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, AnyHttpUrl, constr

class UserBase(BaseModel):
    user_id: UUID = Field(
        default_factory=uuid4,
        description="Unique user identifier.",
        json_schema_extra={"example": "6f8a1d5c-3e6c-4b2d-9c0a-ae7d5f9c1234"},
    )
    email: EmailStr = Field(
        ...,
        description="Login email (unique).",
        json_schema_extra={"example": "user@example.com"},
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Display name (unique).",
        json_schema_extra={"example": "renting_fox"},
    )
    role: Literal["tenant", "landlord", "admin"] = Field(
        "tenant",
        description="Access role.",
        json_schema_extra={"example": "landlord"},
    )
    password_hash: str = Field(
        ...,
        description="Hashed password (e.g. bcrypt).",
        json_schema_extra={"example": "$2b$12$abcdefghijklmNOPQRSTUVWXYZ1234567890"},
    )
    is_active: bool = Field(
        True,
        description="Account active flag.",
        json_schema_extra={"example": True},
    )
    avatar_url: Optional[AnyHttpUrl] = Field(
        None,
        description="Profile avatar URL.",
        json_schema_extra={"example": "https://cdn.example.com/avatars/6f8a1d5c.png"},
    )
    phone: Optional[str] = Field(
        None,
        description="Contact phone number.",
        json_schema_extra={"example": "+1-555-123-4567"},
    )
    bio: Optional[str] = Field(
        None,
        description="Short profile biography.",
        json_schema_extra={"example": "Property enthusiast and long-term host."},
    )
    reputation: float = Field(
        0.0,
        ge=0,
        le=5,
        description="Reputation score (0–5).",
        json_schema_extra={"example": 4.6},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-10T12:00:00Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T09:30:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "6f8a1d5c-3e6c-4b2d-9c0a-ae7d5f9c1234",
                    "email": "landlord@example.com",
                    "username": "prime_host",
                    "role": "landlord",
                    "is_active": True,
                    "avatar_url": "https://cdn.example.com/avatars/prime_host.png",
                    "phone": "+1-555-987-6543",
                    "bio": "Hosting since 2018.",
                    "reputation": 4.9,
                    "created_at": "2025-01-10T12:00:00Z",
                    "updated_at": "2025-01-15T09:30:00Z",
                }
            ]
        }
    }

class UserRegistration(UserBase):
    """Creation payload; ID is generated server-side but present in the base model."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "6f8a1d5c-3e6c-4b2d-9c0a-ae7d5f9c1234",
                    "email": "user@example.com",    
                    "username": "prime_host",
                    "role": "landlord",
                    "is_active": True,
                    "avatar_url": "https://cdn.example.com/avatars/prime_host.png",
                    "phone": "+1-555-987-6543",
                    "bio": "Hosting since 2018.",
                    "reputation": 4.9,
                    "created_at": "2025-01-10T12:00:00Z",
                    "updated_at": "2025-01-10T12:00:00Z",
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    """Partial user update; user_id taken from path. All fields optional."""
    email: Optional[EmailStr] = Field(
        None,
        description="New login email.",
        json_schema_extra={"example": "new_email@example.com"},
    )
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=30,
        description="New display name.",
        json_schema_extra={"example": "updated_host"},
    )
    role: Optional[Literal["tenant", "landlord", "admin"]] = Field(
        None,
        description="Updated access role.",
        json_schema_extra={"example": "admin"},
    )
    password_hash: Optional[str] = Field(
        None,
        description="Replacement hashed password.",
        json_schema_extra={"example": "$2b$12$NEWabcdefghijklmNOPQRSTUVWXYZ1234567890"},
    )
    is_active: Optional[bool] = Field(
        None,
        description="Set account active/inactive.",
        json_schema_extra={"example": False},
    )
    avatar_url: Optional[AnyHttpUrl] = Field(
        None,
        description="Updated avatar URL.",
        json_schema_extra={"example": "https://cdn.example.com/avatars/new.png"},
    )
    phone: Optional[str] = Field(
        None,
        description="Updated contact phone.",
        json_schema_extra={"example": "+1-555-000-1111"},
    )
    bio: Optional[str] = Field(
        None,
        description="Updated biography.",
        json_schema_extra={"example": "Hosting properties worldwide."},
    )
    reputation: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Adjusted reputation score (0–5).",
        json_schema_extra={"example": 4.7},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "new_email@example.com"},
                {"username": "updated_host", "bio": "Hosting properties worldwide."},
                {"is_active": False},
                {"avatar_url": "https://cdn.example.com/avatars/new.png", "phone": "+1-555-000-1111"},
                {"reputation": 4.7},
            ]
        }
    }


class UserRead(UserBase):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-04-10T09:30:00Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-04-12T16:45:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "host@example.com",
                    "username": "host123",
                    "role": "landlord",
                    "is_active": True,
                    "avatar_url": "https://cdn.example.com/avatars/host.png",
                    "phone": "+1-555-123-4567",
                    "bio": "Experienced host with multiple properties.",
                    "reputation": 4.8,
                    "created_at": "2025-04-10T09:30:00Z",
                    "updated_at": "2025-04-12T16:45:00Z",
                }
            ]
        }
    }
