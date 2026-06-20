from datetime import date
from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, status, Response
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
        goal_data: Annotated[GoalCreateForm, Depends(GoalCreateForm.as_form)],
        img: Annotated[UploadFile | None, File()] = None,
        db: Annotated[Session, Depends(get_db)] = None,
        cur_user: Annotated[User, Depends(get_current_user)] = None
):
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
        title: Annotated[str | None, Form()] = None,
        description: Annotated[str | None, Form()] = None,
        link: Annotated[str | None, Form()] = None,
        goal_amount: Annotated[Decimal | None, Form()] = None,
        start_date: Annotated[date | None, Form()] = None,
        end_date: Annotated[date | None, Form()] = None,
        img: Annotated[UploadFile | None, File()] = None
):
    if title == "":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Поле 'title' не может быть пустым!")
    if goal_amount is not None and goal_amount <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Сумма цели должна быть больше нуля!")
    goal_data = {}
    if title is not None: goal_data["title"] = title
    if description is not None: goal_data["description"] = description
    if link is not None: goal_data["link"] = link
    if goal_amount is not None: goal_data["goal_amount"] = goal_amount
    if start_date is not None: goal_data["start_date"] = start_date
    if end_date is not None: goal_data["end_date"] = end_date

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
):
    try:
        services.remove_goal(db, goal_id, cur_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)