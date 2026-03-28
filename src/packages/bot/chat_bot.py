"""
This module contains ChatBot functions associated with answers.
"""
import random
from src.packages.logger import Log, Loggers
# from src.packages.bot.chat_model import ChatModel
from src.packages.loaders import config

__all__ = ["ChatBot"]


class ChatBotException(Exception):
    """
    Class-exception for any errors with bot working.
    """


class ChatBot:
    """
    A chat-bot class with the functionality necessary to generate a response to a user's message.
    """

    _logger: Log

    # _chat_model = ChatModel()

    def __init__(self, logger: Log) -> None:
        """
        Initialize ChatBot class with logger.
        @param logger: custom class responsible for logging.
        """
        self._logger = logger

    def generate_answer(self, text: str) -> str:
        answer = config["start_phrase"]
        self._log_question(text, answer)
        return answer

    def _log_question(self, text: str, intent: str) -> None:
        """
        Logging user question.
        @param text: some question from user.
        @param intent: intent for this question.
        """
        self._logger.info(Loggers.INCOMING.value, f'"{text} — {intent}";')
