from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict, model_validator
from decimal import Decimal
from datetime import date


class GoalBase(BaseModel):
    goal_amount: Decimal
    start_date: date | None
    end_date: date | None


class GoalCreateForm(GoalBase):
    title: str = Field(..., max_length=20)
    description: str | None = Field(default=None, max_length=255)
    link: HttpUrl | None = Field(default=None, max_length=2048)
    # img_path: str | None =  Field(default='images/placeholder.png', max_length=255)

    @field_validator('end_date')
    @classmethod
    def check_correct_end_date(cls, end_date: date | None) -> date | None:
        if (end_date is not None) and (end_date < date.today()):
            raise ValueError('Конечная дата не может быть в прошлом')
        return end_date


class GoalResponse(GoalBase):
    title: str
    description: str | None
    link: str | None
    img_path: str

    model_config = ConfigDict(from_attributes=True)


class GoalWithRaisedResponse(GoalResponse):
    raised: Decimal | None = None


class GoalUpdate(GoalBase):
    title: str | None = None
    description: str | None = None
    link: str | None = None
    img_path: str | None = None
    goal_amount: Decimal | None = None

    @model_validator(mode="before")
    @classmethod
    def check_null_fields(cls, data: dict) -> dict:
        if "title" in data and data["title"] is None:
            raise ValueError("Поле 'title' не может быть пустым!")
        if "goal_amount" in data and data["goal_amount"] is None:
            raise ValueError("Поле 'goal_amount' не может быть пустым!")
        return data