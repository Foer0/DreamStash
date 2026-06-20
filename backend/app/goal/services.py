import shutil
import uuid
import os
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from app.goal.models import Goal
from fastapi import UploadFile
from app.core.config import settings, BASE_DIR

def get_path_to_img(img: UploadFile) -> str:
    upload_path = BASE_DIR / settings.upload_dir
    os.makedirs(upload_path, exist_ok=True)

    file_extension = img.filename.split('.')[-1]
    unique_filename = f'{uuid.uuid4()}.{file_extension}'
    file_system_path = upload_path / unique_filename

    with open(file_system_path, 'wb') as buffer:
        shutil.copyfileobj(img.file, buffer)

    return f"/static/{unique_filename}"


def is_goal_exists(session: Session, goal_id, user_id) -> bool:
    stmt = select(1).where(Goal.id == goal_id, Goal.user_id == user_id)
    return session.scalar(stmt) is not None


def get_active_goals(session: Session, user_id) -> list[Goal]:
    stmt = select(Goal).where(Goal.user_id == user_id, Goal.status == 'Active')
    res = session.execute(stmt)
    return list(res.scalars().all())


def create_new_goal(session: Session, data: dict, img: UploadFile | None) -> Goal:
    if img is not None:
        web_path = get_path_to_img(img)
        data["img_path"] = web_path
    else:
        data["img_path"] = "/static/placeholder.png"

    goal = Goal(**data)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


def update_goal_data(
        session: Session,
        data: dict,
        user_id: int,
        goal_id: int,
        img: UploadFile | None
) -> Goal:
    stmt = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
    goal = session.scalar(stmt)
    if not goal:
        raise ValueError("Goal not found")
    if img is not None:
        new_path = get_path_to_img(img)
        if goal.img_path != settings.placeholder_path and os.path.exists(goal.img_path):
            os.remove(goal.img_path)
        data["img_path"] = new_path

    stmt = (
        update(Goal)
        .where(Goal.user_id == user_id, Goal.id == goal_id)
        .values(**data)
        .returning(Goal)
    )
    res = session.execute(stmt)
    session.commit()
    return res.scalar()


def remove_goal(session: Session, goal_id: int, user_id: int) -> None:
    stmt = delete(Goal).where(Goal.id == goal_id, Goal.user_id == user_id).returning(Goal)
    del_goal = session.execute(stmt).scalar()

    if del_goal is None:
        raise ValueError("Goal not found")
    img_to_delete = del_goal.img_path
    session.commit()

    if img_to_delete is not None and img_to_delete != settings.placeholder_path:
        if os.path.exists(img_to_delete):
            os.remove(img_to_delete)