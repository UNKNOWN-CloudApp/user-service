from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str = Field(
        ...,
        max_length=255,
        description="Login email (primary key).",
        json_schema_extra={"example": "user@example.com"},
    )
    first_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's first name.",
        json_schema_extra={"example": "John"},
    )
    last_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's last name.",
        json_schema_extra={"example": "Doe"},
    )
    token: str = Field(
        ...,
        max_length=255,
        description="Unique authentication token.",
        json_schema_extra={"example": "google-1000000001"},
    )


class UserRegistration(UserBase):
    pass  # UserBase already contains all required fields for registration


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Updated first name.",
        json_schema_extra={"example": "Jane"},
    )
    last_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Updated last name.",
        json_schema_extra={"example": "Smith"},
    )
    token: Optional[str] = Field(
        None,
        max_length=255,
        description="Updated authentication token.",
        json_schema_extra={"example": "google-1000000999"},
    )


class UserRead(UserBase):
    pass  # UserBase contains all fields that can be read