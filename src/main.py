"""
This file is the main one, the bot is launched from it.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append('src')
from src.packages.logger import Log, Loggers
from src.packages.bot.bot import Bot


def main():
    """
    The main function that starts the application.
    """
    logger = Log()
    logger.info(Loggers.APP.value, "Chat-bot session started;")
    bot = Bot(logger)
    bot.start()
    logger.info(Loggers.APP.value, "Chat-bot session ended.")


if __name__ == "__main__":
    main()
