import uuid

from pydantic import BaseModel, EmailStr, Field


class UserSignupPayload(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, min_length=1, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class User(BaseModel):
    id: uuid.UUID
    email: EmailStr
