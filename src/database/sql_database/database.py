import functools

from sqlalchemy.exc import IntegrityError
from typing import List
from sqlalchemy import select

from src.database.sql_database.connection import SessionLocal
from src.database.sql_database.models import UserModel

__all__ = ["SQLDatabase"]

def connect_db(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with SessionLocal() as session:
            out = func(
                *args,
                **kwargs,
                db=session,
            )
        return out
    return wrapper

class SQLDatabase:
    def __init__(self,server):
        self.bot_name = server.bot_name
        self.admin_id_telegram = server.admin_id_telegram
        self.add_user(self.admin_id_telegram)

    def does_the_user_exist(self, telegram_id: int) -> bool:
        return self._get_user_by_telegram_id(telegram_id)

    def find_all_users(self) -> List[int]:
        return self._get_users_by_bot_name()

    def add_user(self, telegram_id: int) -> bool:
        if not self._get_user_by_telegram_id(telegram_id):
            self._add_user(telegram_id)
            return True
        return False

    def remove_user(self, telegram_id: int) -> bool:
        self._delete_user_by_telegram_id(telegram_id)
        return True


    @connect_db
    def _add_user(self,telegram_id,db):
        db_model = UserModel(telegram_id=telegram_id,bot_name=self.bot_name)
        try:
            db.add(db_model)
            db.commit()
        except IntegrityError:
            db.rollback()
        db.refresh(db_model)


    @connect_db
    def _get_users_by_bot_name(self,db):
        return db.query(UserModel).filter(UserModel.bot_name==self.bot_name).all()

    @connect_db
    def _get_user_by_telegram_id(self,telegram_id,db):
        db_object = db.execute(
            select(UserModel).where(
                UserModel.bot_name==self.bot_name,
                UserModel.telegram_id==telegram_id
            )
        )
        return db_object.scalars().first()
    
    @connect_db
    def _delete_user_by_telegram_id(self,telegram_id,db):
        db.query(UserModel).filter(UserModel.bot_name==self.bot_name,UserModel.telegram_id==telegram_id).delete()