from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum
from datetime import date
from decimal import Decimal
from app.user.schemas import Currency


class OperationType(str, Enum):
    DEPOSIT = "deposite"
    WITHDRAW = "withdraw"


class GoalTransaction(BaseModel):
    amount: Decimal
    created_at: date | None = None
    note: str | None = Field(None, max_length=300)

    @field_validator("created_at")
    @classmethod
    def check_date(cls, val) -> date:
        if val and val > date.today():
            raise ValueError("The date cannot be in the future")
        return val


class GoalTransactionResponse(BaseModel):
    user_id: int
    goal_id: int
    amount: Decimal
    currency: Currency
    tx_type: OperationType = Field(alias="type")
    created_at: date
    note: str | None

    model_config = ConfigDict(from_attributes=True)
