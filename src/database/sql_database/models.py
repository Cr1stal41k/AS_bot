from sqlalchemy import String, BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database.sql_database.connection import Base


class UserModel(Base):
    __tablename__ = 'users'

    # Современный стиль Mapped (лучше поддержка IDE и типизации)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Используем BigInteger для безопасности Telegram ID
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    
    bot_name: Mapped[str] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("telegram_id", "bot_name", name="uq_user_bot"),
    )
