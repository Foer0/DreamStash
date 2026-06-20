from pydantic import BaseModel, EmailStr, field_validator, Field, model_validator, ConfigDict
from enum import Enum
from typing import Self
from datetime import date
from decimal import Decimal

MIN_LENGTH_PASS = 8


class Currency(str, Enum):
    USD = "USD"
    BYN = "BYN"
    RUB = "RUB"


class GoogleLoginRequest(BaseModel):
    token: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def check_length_pass(cls, password):
        if len(password) < MIN_LENGTH_PASS:
            raise ValueError("Минимальная длина пароля 8 символов")
        return password


class UserResponse(BaseModel):
    email: str
    currency: Currency

    model_config = ConfigDict(from_attributes=True)


class UpdateUserInfo(BaseModel):
    passwd: str | None = None
    new_passwd: str | None = Field(None, min_length=MIN_LENGTH_PASS)
    confirm_passwd: str | None = None
    email: EmailStr | None = None
    currency: Currency | None = None

    @model_validator(mode="after")
    def check_passwd_change(self) -> Self:
        has_old = self.passwd is not None
        has_new = self.new_passwd is not None
        has_confirm = self.confirm_passwd is not None

        # Попытка сменить пароль — заполнено new_passwd или confirm_passwd
        if has_new or has_confirm:
            if not (has_old and has_new and has_confirm):
                raise ValueError(
                    "To change the password, you need to fill in the current password, "
                    "the new password, and the confirmation"
                )
            if self.new_passwd != self.confirm_passwd:
                raise ValueError("The passwords don't match")
            if self.passwd == self.new_passwd:
                raise ValueError("The new password must not match the old one")
        return self


class GoalLogResponse(BaseModel):
    id: int
    created_at: date
    goal_title: str
    amount: Decimal
    currency: str
    operation_type: str
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedHistoryResponse(BaseModel):
    items: list[GoalLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
