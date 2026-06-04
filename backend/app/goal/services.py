import shutil
import uuid
import os
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import Session
from app.goal.models import Goal
from app.goal_log.models import GoalLog
from app.core.config import settings
from fastapi import UploadFile
from decimal import Decimal


def get_goals(session: Session, user_id: int) -> list[tuple[Goal, Decimal | None]]:
    sql_expr = (
        select(Goal, func.sum(GoalLog.amount).label('raised'))
        .join(GoalLog, Goal.id == GoalLog.goal_id, isouter=True)
        .where(Goal.user_id == user_id)
        .group_by(Goal.id)
    )
    rows = session.execute(sql_expr).all()
    return [(row.Goal, row.raised) for row in rows]


def create_new_goal(session: Session, data: dict, img: UploadFile) -> Goal:

    file_extension = img.filename.split('.')[-1]
    unique_filename = f'{uuid.uuid4()}{file_extension}'
    file_path = os.path.join(settings.upload_dir, unique_filename)
    data[Goal.img_path.key] = file_path

    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(img.file, buffer)

    goal = Goal(**data)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


def update_goal_data(session: Session, data: dict, user_id: int, goal_id: int) -> Goal:
    stmt = (
        update(Goal)
        .where(Goal.user_id == user_id, Goal.id == goal_id)
        .values(data)
        .returning(Goal)
    )
    res = session.execute(stmt)
    session.commit()
    return res.scalar()


def is_goal_exists(session: Session, goal_id, user_id) -> bool:
    stmt = select(1).where(Goal.id == goal_id, Goal.user_id == user_id)
    return session.scalar(stmt) is not None


def remove_goal(session: Session, goal_id: int, user_id: int) -> None:
    stmt = delete(Goal).where(Goal.id == goal_id, Goal.user_id==user_id)
    session.execute(stmt)
    session.commit()
