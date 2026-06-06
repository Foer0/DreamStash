from typing import Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, status
from app.dependencies import get_db, get_current_user
from sqlalchemy.orm import Session
from app.goal_log.schemas import GoalTransaction, GoalTransactionResponse, OperationType
from app.goal_log import services
from app.goal.services import is_goal_exists
from app.user.models import User


router = APIRouter()


@router.post("/goals/{goal_id}/operation/{type}", status_code=201, response_model=GoalTransactionResponse)
def process_transaction(
        goal_id: int,
        tx_type: Annotated[OperationType, Path(alias="type")],
        tx_data: GoalTransaction,
        db: Annotated[Session, Depends(get_db)],
        cur_user: Annotated[User, Depends(get_current_user)]
):
    if not is_goal_exists(db, goal_id, cur_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    tx = tx_data.model_dump(exclude_none=True)
    tx["user_id"] = cur_user.id
    tx["goal_id"] = goal_id
    tx["type"] = tx_type
    tx["currency"] = cur_user.currency
    db_log = services.add_tx(db, tx)
    return GoalTransactionResponse.model_validate(db_log)


