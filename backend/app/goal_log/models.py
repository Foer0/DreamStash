from app.core.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Identity, Numeric, CHAR, Date, Text, ForeignKey, CheckConstraint, text
from decimal import Decimal
from datetime import date
from app.user.schemas import Currency


class GoalLog(Base):
    __tablename__ = 'goal_logs'
    __table_args__ = (
        CheckConstraint("type IN ('deposite', 'withdraw')"),
        CheckConstraint("created_at <= CURRENT_DATE"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key = True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    goal_id: Mapped[int] = mapped_column(Integer, ForeignKey('goals.id', ondelete='CASCADE'))
    amount: Mapped[Decimal] = mapped_column(Numeric(11, 2))
    currency: Mapped[Currency] = mapped_column(CHAR(3))
    operation_type: Mapped[str] = mapped_column(CHAR(8), name="type")
    created_at: Mapped[date] = mapped_column(Date, server_default=text('CURRENT_DATE'))
    note: Mapped[str | None] = mapped_column(Text)

    user: Mapped['User'] = relationship(back_populates='goal_logs')
    goal: Mapped['Goal'] = relationship(back_populates='goal_logs')
