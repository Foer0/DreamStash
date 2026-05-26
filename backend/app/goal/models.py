from app.core.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, Identity, String, Date, Numeric, ForeignKey, CheckConstraint
from datetime import date
from decimal import Decimal


class Goal(Base):
    __tablename__ = 'goals'
    __table_args__ = (
        CheckConstraint('end_date >= CURRENT_DATE'),
        CheckConstraint('status IN (\'Active\', \'Done\')'),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(String(255), default=None)
    link: Mapped[str | None] = mapped_column(String(2048), default=None)
    img_path: Mapped[str | None] = mapped_column(String(255), default='./backend/images/placeholder.png')
    goal_amount: Mapped[Decimal] = mapped_column(Numeric(11, 2))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default='Active')

    user: Mapped['User'] = relationship(back_populates='goals')
    goal_logs: Mapped[list['GoalLog']] = relationship(back_populates='goal')
