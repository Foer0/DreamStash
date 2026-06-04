from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from app.goal.schemas import GoalCreateForm, GoalWithRaisedResponse, GoalUpdate, GoalResponse
from app.dependencies import get_db, get_current_user_id
from app.goal import services


UPLOAD_DIR = "backend"

router = APIRouter()


@router.get("/goals", response_model=list[GoalWithRaisedResponse])
def display_goals(
        db: Annotated[Session, Depends(get_db)],
        cur_user_id: Annotated[int, Depends(get_current_user_id)]
):
    rows = services.get_goals(db, cur_user_id)
    goals_out = []
    for goal, raised in rows:
        schema = GoalWithRaisedResponse.model_validate(goal)
        schema.raised = raised
        goals_out.append(schema)

    return goals_out



@router.post("/goals", response_model=GoalWithRaisedResponse)
def create_goal(
        goal_data: Annotated[GoalCreateForm, Form()],
        img: Annotated[UploadFile | None, File()],
        db: Annotated[Session, Depends(get_db)],
        cur_user_id: Annotated[int, Depends(get_current_user_id)]
):
    """
       Возможно добавить проверку что если у пользователя нет токена авторизации,
       то просто создавать задачу после проверки Pydantic, но ничего не сохранять в БД
    """
    goal = goal_data.model_dump()
    goal["user_id"] = cur_user_id
    new_goal_out = services.create_new_goal(session=db, data=goal, img=img)
    return GoalWithRaisedResponse.model_validate(new_goal_out)


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(
        goal_id: int,
        db: Annotated[Session, Depends(get_db)],
        cur_user_id: Annotated[int, Depends(get_current_user_id)],
        goal: GoalUpdate
):
    if not services.is_goal_exists(db, goal_id, cur_user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    goal_data = goal.model_dump(exclude_unset=True)
    upd_goal = services.update_goal_data(db, goal_data, cur_user_id, goal_id)
    return GoalResponse.model_validate(upd_goal)


@router.delete("goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
        goal_id: int,
        db: Annotated[Session, Depends(get_db)],
        cur_user_id: Annotated[int, Depends(get_current_user_id)]
) -> None:
    if not services.is_goal_exists(db, goal_id, cur_user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    services.remove_goal(db, goal_id, cur_user_id)
    return



