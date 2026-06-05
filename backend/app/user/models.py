from app.core.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Identity, String, Text, CHAR, TIMESTAMP, CheckConstraint, ForeignKey
from datetime import datetime
from app.user.schemas import Currency


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("LENGTH(hashed_password) >= 8"),
        CheckConstraint("currency IN ('USD', 'RUB', 'BYN')"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(CHAR(3), default=Currency.USD)

    refresh_tokens: Mapped[list["UserRefreshToken"]] = relationship(back_populates="user")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user")
    goal_logs: Mapped[list["GoalLog"]] = relationship(back_populates="user")


class UserRefreshToken(Base):
    __tablename__ = "user_refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(Text, unique=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")