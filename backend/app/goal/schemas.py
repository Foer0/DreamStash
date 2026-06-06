from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict, model_validator
from decimal import Decimal
from datetime import date
from app.user.schemas import Currency


class GoalBase(BaseModel):
    goal_amount: Decimal
    start_date: date | None
    end_date: date | None


class GoalCreateForm(GoalBase):
    title: str = Field(..., max_length=20)
    description: str | None = Field(default=None, max_length=255)
    link: HttpUrl | None = Field(default=None, max_length=2048)

    @field_validator('end_date')
    @classmethod
    def check_correct_end_date(cls, end_date: date | None) -> date | None:
        if (end_date is not None) and (end_date < date.today()):
            raise ValueError('Конечная дата не может быть в прошлом')
        return end_date


class GoalBaseResponse(BaseModel):
    id: int
    title: str
    description: str | None
    link: str | None
    img_path: str
    start_date: date | None
    end_date: date | None
    goal_amount: Decimal


class GoalResponse(GoalBaseResponse):
    current_amount: Decimal # накопленно, отображение в currency
    currency: str           # валюта в которой видет пользователь


class GoalCreateUpdateResponse(GoalBaseResponse):
    target_currency: Currency
    status: str

    model_config = ConfigDict(from_attributes=True)


class GoalUpdate(GoalBase):
    title: str | None = None
    description: str | None = None
    link: str | None = None
    goal_amount: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="before")
    @classmethod
    def check_null_fields(cls, data: dict) -> dict:
        if "title" in data and data["title"] is None:
            raise ValueError("Поле 'title' не может быть пустым!")
        if "goal_amount" in data and data["goal_amount"] is None:
            raise ValueError("Поле 'goal_amount' не может быть пустым!")
        return data