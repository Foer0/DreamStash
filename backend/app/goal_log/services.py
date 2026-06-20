from sqlalchemy import insert, func, select, case
from sqlalchemy.orm import Session
from app.goal_log.models import GoalLog
from app.goal_log.schemas import OperationType
from decimal import Decimal
from app.user.schemas import Currency
from app.core.rates import convert
from app.goal.models import Goal
from sqlalchemy import case, func, update as sa_update


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


def get_goal_net_balance(session: Session, goal_id: int, user_currency: str) -> Decimal:
    stmt = (
        select(
            GoalLog.currency,
            func.sum(case(
                (GoalLog.operation_type == 'deposit', GoalLog.amount),
                else_=Decimal('0')
            )).label('deposits'),
            func.sum(case(
                (GoalLog.operation_type == 'withdraw', GoalLog.amount),
                else_=Decimal('0')
            )).label('withdrawals')
        )
        .where(GoalLog.goal_id == goal_id)
        .group_by(GoalLog.currency)
    )
    rows = session.execute(stmt).all()
    total = Decimal('0')
    for currency, deposits, withdrawals in rows:
        net = (deposits or Decimal('0')) - (withdrawals or Decimal('0'))
        total += convert(net, currency, user_currency)  # уже используется в роутере
    return total


def update_goal_status(session: Session, goal_id: int, new_status: str) -> None:
    session.execute(sa_update(Goal).where(Goal.id == goal_id).values(status=new_status))
    session.commit()


def get_goal_by_id(session: Session, goal_id: int, user_id: int) -> Goal | None:
    return session.scalar(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
    )

