"""
This module contains ChatBot functions associated with answers.
"""
import random
from src.packages.logger import Log, Loggers
from src.packages.bot.chat_model import ChatModel
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
    _chat_model = ChatModel()

    def __init__(self, logger: Log) -> None:
        """
        Initialize ChatBot class with logger.
        @param logger: custom class responsible for logging.
        """
        self._logger = logger

    def generate_answer(self, text: str) -> str:
        """
        Initialize ChatBot class with logger.
        @param text: some question from user.
        @return: return user text.
        """
        intent = self._get_question_intent(text)
        self._log_question(text, intent)

        if intent is not None:
            return self._get_random_answer_by_intent(intent)
        return self._get_reserve_answer()

    @staticmethod
    def _get_random_answer_by_intent(intent: str) -> str:
        """
        Getting random answer for specific intent.
        @param intent: intent for user question.
        @return: random selected response for question.
        """
        responses = config["intents"][intent]["responses"]
        return random.choice(responses)

    @staticmethod
    def _get_reserve_answer() -> str:
        """
        Getting reserve answer, return failure phrase from `bot_config`.
        @return: string with reserve answer.
        """
        answer = random.choice(config["failure_phrases"])
        return answer

    def _get_question_intent(self, text: str) -> str or None:
        """
        Getting intent for user question.
        @param text: some question from user.
        @return: some intent for question.
        """
        try:
            return self._chat_model.get_intent(text)
        # pylint: disable=W0703:
        except Exception as exception:
            ChatBotException(f"Unexpected error: {exception}")
            return None

    def _log_question(self, text: str, intent: str) -> None:
        """
        Logging user question.
        @param text: some question from user.
        @param intent: intent for this question.
        """
        self._logger.info(Loggers.INCOMING.value, f'"{text} — {intent}";')
