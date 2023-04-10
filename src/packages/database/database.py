"""
Database module.
"""
from typing import List
import pandas as pd
from packages.path_storage.path_storage import PathStorage
from packages.loaders import env_variables

__all__ = ["Database"]


class DatabaseException(Exception):
    """
    Exception class for the `Database`.
    """


class Database:
    """
    Database class. This class contains the necessary methods
    for working with a database implemented simply in a file.
    """

    _path_to_db_file: str
    _DB_FILE_SEP = ","
    _DB_FILE_ENCODING = "utf-8"
    _COLUMN_TELEGRAM_ID = "Telegram_ID"

    def __init__(self, path_to_db_file):
        self._path_to_db_file = path_to_db_file
        if not PathStorage.does_file_exists(self._path_to_db_file):
            self._init_db_file()

    def _init_db_file(self):
        """
        Initializes the database file if it does not exist.
        The database will have a single entry – the admin id.
        """
        database = pd.DataFrame(columns=[self._COLUMN_TELEGRAM_ID])
        database.loc[len(database.index)] = env_variables["ADMIN_ID_TELEGRAM"]
        self._save_db_file(database)

    def _load_db_file(self) -> pd.DataFrame:
        """
        @return: uploaded database file in `pd.DataFrame` format.
        """
        try:
            return pd.read_csv(self._path_to_db_file, sep=self._DB_FILE_SEP, encoding=self._DB_FILE_ENCODING)
        except FileNotFoundError as exception:
            raise DatabaseException(f"Can't find db file: {exception}.") from exception
        except Exception as exception:
            raise DatabaseException(f"Unexpected error: {exception}.") from exception

    def _save_db_file(self, database: pd.DataFrame):
        """
        Saves the passed `pd.DataFrame` to a database file.
        @param database: `pd.DataFrame` to be saved
        """
        try:
            database.to_csv(self._path_to_db_file, sep=self._DB_FILE_SEP, encoding=self._DB_FILE_ENCODING, index=False)
        except Exception as exception:
            raise DatabaseException(f"Unexpected error: {exception}.") from exception

    def does_the_user_exist(self, telegram_id: int) -> bool:
        """
        Check for the existence of a user by the specified id.
        @param telegram_id: id of the user to check for existence in the database.
        """
        database = self._load_db_file()
        return len(database[database[self._COLUMN_TELEGRAM_ID] == telegram_id].values) > 0

    def find_all_users(self) -> List[int]:
        """
        @return: all users from the database.
        """
        database = self._load_db_file()
        return list(database[self._COLUMN_TELEGRAM_ID].values)

    def add_user(self, telegram_id: int) -> bool:
        """
        Adds a user to the database.
        @param telegram_id: id of the user to add.
        @return: `True` if it was possible to add, otherwise `False`.
        """
        database = self._load_db_file()
        if self.does_the_user_exist(telegram_id):
            return False
        database.loc[len(database.index)] = telegram_id
        self._save_db_file(database)
        return True

    def remove_user(self, telegram_id: int) -> bool:
        """
        Delete a user from the database.
        @param telegram_id: id of the user to delete.
        @return: `True` if it was possible to delete, otherwise `False`.
        """
        database = self._load_db_file()
        if not self.does_the_user_exist(telegram_id):
            return False
        database = database[database[self._COLUMN_TELEGRAM_ID] != telegram_id]
        self._save_db_file(database)
        return True
