from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from app.goal.schemas import GoalCreateForm, GoalCreateUpdateResponse, GoalResponse, GoalUpdate
from app.dependencies import get_db, get_current_user
from app.goal import services
from app.goal_log.services import get_total_goal_tx
from app.goal.models import Goal
from app.user.models import User
from decimal import Decimal
from app.core.rates import convert


UPLOAD_DIR = "backend"

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.get("/", response_model=list[GoalResponse])
def display_goals(
        db: Annotated[Session, Depends(get_db)],
        cur_user: Annotated[User, Depends(get_current_user)]
):
    active_goals: list[Goal] = services.get_active_goals(db, cur_user.id)
    goal_ids: list[int] = [g.id for g in active_goals]
    subtotals = get_total_goal_tx(db, goal_ids)

    goal_subtotals = {}
    for row in subtotals:
        goal_subtotals.setdefault(row[0], []).append((row[1], row[2]))

    user_currency = cur_user.currency
    result = []

    for goal in active_goals:
        total = Decimal("0")
        for curr, sub in goal_subtotals.get(goal.id, []):
            total += convert(sub, curr, user_currency)

        goal_amount_converted = convert(goal.goal_amount, goal.target_currency, user_currency)

        result.append(GoalResponse(
            id=goal.id,
            title=goal.title,
            description=goal.description,
            link=goal.link,
            img_path=goal.img_path,
            start_date=goal.start_date,
            end_date=goal.end_date,
            goal_amount=goal_amount_converted,
            currency=user_currency,
            current_amount=total
        ))

    return result


@router.post("/", response_model=GoalCreateUpdateResponse)
def create_goal(
        goal_data: Annotated[GoalCreateForm, Form()],
        img: Annotated[UploadFile | None, File()],
        db: Annotated[Session, Depends(get_db)],
        cur_user: Annotated[User, Depends(get_current_user)]
):
    """
       Возможно добавить проверку что если у пользователя нет токена авторизации,
       то просто создавать задачу после проверки Pydantic, но ничего не сохранять в БД
    """
    goal = goal_data.model_dump()
    goal["user_id"] = cur_user.id
    goal["target_currency"] = cur_user.currency
    new_goal_out = services.create_new_goal(session=db, data=goal, img=img)
    return GoalCreateUpdateResponse.model_validate(new_goal_out)


@router.patch("/{goal_id}", response_model=GoalCreateUpdateResponse)
def update_goal(
        goal_id: int,
        db: Annotated[Session, Depends(get_db)],
        cur_user: Annotated[User, Depends(get_current_user)],
        goal: GoalUpdate,
        img: Annotated[UploadFile | None, File()] = None
):
    goal_data = goal.model_dump(exclude_unset=True)
    try:
        upd_goal = services.update_goal_data(db, goal_data, cur_user.id, goal_id, img)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return GoalCreateUpdateResponse.model_validate(upd_goal)



@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
        goal_id: int,
        db: Annotated[Session, Depends(get_db)],
        cur_user: Annotated[User, Depends(get_current_user)]
) -> None:
    try:
        services.remove_goal(db, goal_id, cur_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return