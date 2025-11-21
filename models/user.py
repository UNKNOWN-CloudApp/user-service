from __future__ import annotations

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Display name (unique).",
        json_schema_extra={"example": "renting_fox"},
    )
    email: str = Field(
        ...,
        max_length=100,
        description="Login email (unique).",
        json_schema_extra={"example": "user@example.com"},
    )
    first_name: str = Field(
        ...,
        max_length=50,
        description="User's first name.",
        json_schema_extra={"example": "John"},
    )
    last_name: str = Field(
        ...,
        max_length=50,
        description="User's last name.",
        json_schema_extra={"example": "Doe"},
    )
    role: Literal["tenant", "landlord", "admin"] = Field(
        "tenant",
        description="Access role.",
        json_schema_extra={"example": "landlord"},
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
    reputation_score: float = Field(
        0.00,
        ge=0,
        le=5,
        description="Reputation score (0–5).",
        json_schema_extra={"example": 4.6},
    )
    review_count: int = Field(
        0,
        ge=0,
        description="Number of reviews received.",
        json_schema_extra={"example": 10},
    )

class UserRegistration(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="User password (will be hashed).",
        json_schema_extra={"example": "securepassword123"},
    )


class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New display name.",
        json_schema_extra={"example": "updated_user"},
    )
    email: Optional[str] = Field(
        None,
        max_length=100,
        description="New login email.",
        json_schema_extra={"example": "new_email@example.com"},
    )
    first_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated first name.",
        json_schema_extra={"example": "Jane"},
    )
    last_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated last name.",
        json_schema_extra={"example": "Smith"},
    )
    role: Optional[Literal["tenant", "landlord", "admin"]] = Field(
        None,
        description="Updated access role.",
        json_schema_extra={"example": "admin"},
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Updated contact phone.",
        json_schema_extra={"example": "+1-555-000-1111"},
    )
    bio: Optional[str] = Field(
        None,
        description="Updated biography.",
        json_schema_extra={"example": "Hosting properties worldwide."},
    )
    reputation_score: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Adjusted reputation score (0–5).",
        json_schema_extra={"example": 4.7},
    )
    review_count: Optional[int] = Field(
        None,
        ge=0,
        description="Updated review count.",
        json_schema_extra={"example": 15},
    )


class UserRead(UserBase):
    id: int = Field(
        ...,
        description="Unique user ID (auto-generated).",
        json_schema_extra={"example": 123},
    )
    password_hash: str = Field(
        ...,
        description="Hashed password (e.g. bcrypt).",
        json_schema_extra={"example": "$2b$12$abcdefghijklmNOPQRSTUVWXYZ1234567890"},
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp.",
        json_schema_extra={"example": "2025-01-10T12:00:00Z"},
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp.",
        json_schema_extra={"example": "2025-01-15T09:30:00Z"},
    )

