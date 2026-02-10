import os

from core.base_config import MixinSettings


class SqlConnectConfig(MixinSettings):
    # Example for SQLite
    database_url: str = f"sqlite:///{os.getcwd()}/src/db/sql_lite.db"


sql_con_config = SqlConnectConfig()