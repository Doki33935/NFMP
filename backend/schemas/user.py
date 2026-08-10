from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


Role = Literal["dispatcher", "inspector", "admin", "chief"]


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=12, max_length=128)
    password_confirmation: str
    role: Role
    full_name: str = Field(min_length=2, max_length=255)

    @field_validator("username", "full_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value is required")
        return value

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[Role] = None
    password: Optional[str] = Field(None, min_length=12, max_length=128)
    password_confirmation: Optional[str] = None

    @field_validator("username", "full_name")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password is not None and self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self


class PasswordChange(BaseModel):
    current_password: Optional[str] = None
    new_password: str = Field(min_length=12, max_length=128)
    password_confirmation: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self
