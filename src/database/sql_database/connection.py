from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

from src.core.database_config import sql_con_config


SQLALCHEMY_DATABASE_URL = sql_con_config.database_url


# Создаем асинхронный движок
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)

# Фабрика сессий
SessionLocal = sessionmaker(
    autoflush=False,
    bind=engine, 
)

class Base(DeclarativeBase):
    pass
