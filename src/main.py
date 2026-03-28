"""
This file is the main one, the bot is launched from it.
"""
import sys
import os
import threading

from aiogram import Bot as Telegram_bot

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append('src')
from src.packages.logger import Log
from src.packages.bot.bot import Bot
from src.core.config import servers_config
from src.packages.email_checker import EmailCheckerOutlook
from src.database.sql_database.database import SQLDatabase

def main():
    """
    The main function that starts the application.
    """
    logger = Log()
    threads = list()
    for server in servers_config:
        telegram_bot = Telegram_bot(server.api_key_telegram)
        email_checker = EmailCheckerOutlook(server.email_service_host, server.email_login, server.email_password)
        sql_database = SQLDatabase(server=server)
        bot = Bot(logger,bot=telegram_bot,email_checker=email_checker,server=server,db=sql_database)
        thread = threading.Thread(target=bot.start)
        thread.start()
        threads.append(thread)

    # Обязательно ждем, чтобы основной поток не закрылся!
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
