from sqlalchemy import insert, func, select, case
from sqlalchemy.orm import Session
from app.goal_log.models import GoalLog
from app.goal_log.schemas import OperationType
from decimal import Decimal
from app.user.schemas import Currency


def add_tx(session: Session, tx_data: dict) -> GoalLog:
    stmt = insert(GoalLog).values(**tx_data).returning(GoalLog)
    res = session.scalar(stmt)
    session.commit()
    return res


def get_total_goal_tx(session: Session, goal_ids: list[int]) -> list[tuple[int, Currency, Decimal]]:
    amount_expr = case(
        (GoalLog.operation_type == OperationType.WITHDRAW, -GoalLog.amount),
        else_=GoalLog.amount
    )
    stmt = (
        select(
            GoalLog.goal_id,
            GoalLog.currency,
            func.sum(amount_expr).label("subtotal")
        )
        .where(GoalLog.goal_id.in_(goal_ids))
        .group_by(GoalLog.goal_id, GoalLog.currency)
    )
    res = session.execute(stmt).all()
    return [(row[0], Currency(row[1]), Decimal(str(row[2] or 0))) for row in res]



