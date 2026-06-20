from typing import Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, status
from app.dependencies import get_db, get_current_user
from sqlalchemy.orm import Session
from app.goal_log.schemas import GoalTransaction, GoalTransactionResponse, OperationType
from app.goal_log import services
from app.user.models import User
from app.core.rates import convert


router = APIRouter()


@router.post("/goals/{goal_id}/operation/{type}", status_code=201, response_model=GoalTransactionResponse)
def process_transaction(
        goal_id: int,
        tx_type: Annotated[OperationType, Path(alias="type")],
        tx_data: GoalTransaction,
        db: Annotated[Session, Depends(get_db)],
        cur_user: Annotated[User, Depends(get_current_user)]
):
    goal = services.get_goal_by_id(db, goal_id, cur_user.id)  # ← заменяет is_goal_exists
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    if tx_type == OperationType.WITHDRAW:
        balance = services.get_goal_net_balance(db, goal_id, cur_user.currency)
        if tx_data.amount > balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недостаточно средств. Текущий баланс: {balance:.2f} {cur_user.currency}"
            )

    tx = tx_data.model_dump(exclude_none=True)
    tx["user_id"] = cur_user.id
    tx["goal_id"] = goal_id
    tx["operation_type"] = tx_type.value
    tx["currency"] = cur_user.currency

    db_log = services.add_tx(db, tx)

    if tx_type == OperationType.DEPOSIT:
        new_balance = services.get_goal_net_balance(db, goal_id, cur_user.currency)
        goal_amount_in_user_currency = convert(goal.goal_amount, goal.target_currency, cur_user.currency)
        if new_balance >= goal_amount_in_user_currency:
            services.update_goal_status(db, goal_id, 'Done')

    return GoalTransactionResponse.model_validate(db_log)


