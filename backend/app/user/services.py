from sqlalchemy.orm import Session
from sqlalchemy import select, insert, and_, update, delete
from app.user.models import User, UserRefreshToken
from app.user.schemas import UserRegister, Currency
from app.core.security.password import hash_password, verify_password
from datetime import datetime
from app.goal_log.models import GoalLog
from app.goal.models import Goal
from app.core.rates import convert
from decimal import Decimal
from typing import Optional
from datetime import date as date_type


class InvalidCredentialsError(Exception): ...


def get_user(session: Session, user_id) -> User:
    stmt = select(User).where(User.id == user_id)
    return session.scalar(stmt)


def get_user_by_email(session: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return session.scalar(stmt)


def create_oauth_user(session: Session, email: str) -> User:
    db_user = User(
        email=email,
        hashed_password=None,
        currency=Currency.USD
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def is_user_exist(session: Session, user_email) -> bool:
    stmt = select(1).where(User.email == user_email).limit(1)
    return session.scalar(stmt) is not None


def create_user(session: Session, user_data: UserRegister) -> None:
    hashed_password = hash_password(user_data.password)
    user_dict = user_data.model_dump(exclude={"password"})
    stmt = insert(User).values(**user_dict, hashed_password=hashed_password)
    session.execute(stmt)
    session.commit()


def authenticate_user(session: Session, email, password) -> User:
    stmt = select(User).where(User.email == email)
    user = session.scalar(stmt)

    if user is None:
        raise InvalidCredentialsError("Неверный логин или пароль")
    if user.hashed_password is None:
        raise InvalidCredentialsError("Этот аккаунт зарегистрирован через Google. Используйте вход через Google.")
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Неверный логин или пароль")

    return user


def save_refresh_token_to_db(session: Session, user_id: int, token: str, exp: datetime) -> None:
    session.execute(delete(UserRefreshToken).where(UserRefreshToken.user_id == user_id))
    stmt = insert(UserRefreshToken).values(user_id=user_id, token=token, expires_at=exp)
    session.execute(stmt)
    session.commit()


def has_refresh_token(session: Session, token: str, user_id: int) -> bool:
    stmt = select(1).where(
        and_(
            UserRefreshToken.token == token,
            UserRefreshToken.user_id == user_id
        )
    )
    return session.scalar(stmt) is not None


def update_user(session: Session, user: User, update_data: dict) -> User:
    if "email" in update_data or "new_passwd" in update_data:
        current_password = update_data.pop("passwd")
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Invalid password")

    if "new_passwd" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("new_passwd"))

    stmt = (
        update(User)
        .where(User.id == user.id)
        .values(**update_data)
        .returning(User)
    )
    res = session.execute(stmt)
    session.commit()
    return res.scalar()


def get_user_history(
        session: Session,
        cur_user: User,
        goal: Optional[str] = None,
        date_from: Optional[date_type] = None,
        date_to: Optional[date_type] = None,
        operation_type: Optional[str] = None,
        amount_from: Optional[Decimal] = None,
        amount_to: Optional[Decimal] = None,
        sort_by: str = "date",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 10,
) -> dict:
    stmt = (
        select(
            GoalLog.id,
            GoalLog.created_at,
            Goal.title.label("goal_title"),
            GoalLog.amount,
            GoalLog.currency,
            GoalLog.operation_type,
            GoalLog.note,
        )
        .join(Goal, GoalLog.goal_id == Goal.id)
        .where(GoalLog.user_id == cur_user.id)
    )

    if goal:
        stmt = stmt.where(Goal.title.ilike(f"%{goal}%"))
    if date_from:
        stmt = stmt.where(GoalLog.created_at >= date_from)
    if date_to:
        stmt = stmt.where(GoalLog.created_at <= date_to)
    if operation_type in ("deposit", "withdraw"):
        stmt = stmt.where(GoalLog.operation_type == operation_type)

    rows = session.execute(stmt).all()

    history = []
    for row in rows:
        amount_decimal = (
            Decimal(str(row.amount))
            if not isinstance(row.amount, Decimal)
            else row.amount
        )
        converted = convert(amount_decimal, row.currency, cur_user.currency)
        rounded = converted.quantize(Decimal("0.00"))
        history.append(
            {
                "id": row.id,
                "created_at": row.created_at,
                "goal_title": row.goal_title,
                "amount": rounded,
                "currency": cur_user.currency,
                "operation_type": row.operation_type,
                "note": row.note,
            }
        )

    if amount_from is not None:
        history = [h for h in history if h["amount"] >= Decimal(str(amount_from))]
    if amount_to is not None:
        history = [h for h in history if h["amount"] <= Decimal(str(amount_to))]

    reverse = sort_dir == "desc"
    sort_map = {
        "goal": lambda x: x["goal_title"].lower(),
        "total": lambda x: x["amount"],
        "type": lambda x: x["operation_type"].lower(),
    }
    key_fn = sort_map.get(sort_by, lambda x: (x["created_at"], x["id"]))
    history.sort(key=key_fn, reverse=reverse)

    total = len(history)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    items = history[start: start + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }



