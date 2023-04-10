"""
Bot module.
"""
from typing import List
import asyncio
from aiogram import Bot as Telegram_bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound

from src.packages.bot.chat_bot import ChatBot
from src.packages.email_checker.email_checker_outlook import EmailCheckerOutlookException
from src.packages.logger.logger import Log, Loggers
from src.packages.loaders import config, env_variables
from src.packages.email_checker import EmailCheckerOutlook
from src.packages.message.message import MessageException
from src.packages.parser import Parser
from src.packages.message import Message
from src.packages.parser.parser import ParserException
from src.packages.path_storage import PathStorage
from src.packages.database import Database

__all__ = ["Bot"]


def _parse_command(message: types.Message):
    message_text = message.text
    params = message_text.split(" ")
    params.pop(0)
    return params


class Bot:
    """
    Bot class.Implements all the necessary handlers for the telegram messenger.
    """

    _chat_bot: ChatBot
    _logger: Log
    _email_checker = None
    _db: Database
    bot: Telegram_bot
    _dp: Dispatcher

    def __init__(self, logger: Log) -> None:
        """
        Initialize Bot object.
        @param logger: custom class responsible for logging.
        """
        self._chat_bot = ChatBot(logger)
        self._logger = logger
        self._email_checker = EmailCheckerOutlook(
            env_variables["EMAIL_SERVICE_HOST"], env_variables["EMAIL_LOGIN"], env_variables["EMAIL_PASSWORD"]
        )
        self._db = Database(PathStorage.get_path_to_database_file())
        self.bot = Telegram_bot(env_variables["API_KEY_TELEGRAM"])
        self._dp = Dispatcher(self.bot)
        self._register_handlers()

    @staticmethod
    def _private_chat_guard(func):
        """
        A decorator that runs the decorated function only for
        private chats, otherwise it displays a prepared message.
        @param func: decorated function.
        @return: wrapper.
        """

        async def wrapper(self, message: types.Message):
            if message.chat.type != "private":
                await self.bot.send_message(message.from_user.id, config["only_for_private_chat"])
                return
            await func(self, message)

        return wrapper

    @staticmethod
    def _admin_guard(func):
        """
        A decorator that runs the decorated function only for
        admin user, otherwise it displays a prepared message.
        @param func: decorated function.
        @return: wrapper.
        """

        async def wrapper(self, message: types.Message):
            if str(message.from_user.id) != env_variables["ADMIN_ID_TELEGRAM"]:
                await self.bot.send_message(message.from_user.id, config["only_for_admin"])
                return
            await func(self, message)

        return wrapper

    async def _handle_start(self, message: types.Message):
        """
        This handler will be called when user sends `/start` command.
        """
        await self.bot.send_message(message.from_user.id, config["start_phrase"])

    async def _handle_help(self, message: types.Message):
        """
        This handler will be called when user sends `/help` command.
        """
        await self.bot.send_message(message.from_user.id, config["help_phrase"])

    @_private_chat_guard
    async def _handle_my_id(self, message: types.Message):
        """
        This handler will be called when user sends `/my_id` command.
        """
        await self.bot.send_message(message.from_user.id, message.from_user.id)

    @_private_chat_guard
    @_admin_guard
    async def _handle_add_user(self, message: types.Message):
        """
        This handler will be called when user sends `/add_user` command.
        """
        telegram_ids = _parse_command(message)
        if len(telegram_ids) == 0:
            await self.bot.send_message(message.from_user.id, config["user_id_not_specified"])
        for telegram_id in telegram_ids:
            try:
                telegram_id = int(telegram_id)
                if telegram_id < 0:
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Пользователь с id={telegram_id} не добавлен, так как id не может быть отрицательным.",
                    )
                    return
                if not self._db.add_user(telegram_id):
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Пользователь с id={telegram_id} не добавлен, так как он уже находится в базе данных.",
                    )
                    return
                await self.bot.send_message(
                    message.from_user.id,
                    f"Пользователь с id={telegram_id} добавлен.",
                )
            except ValueError:
                await self.bot.send_message(message.from_user.id, config["id_contains_more_than_just_numbers"])
            except Exception as exception:  # pylint: disable=W0703
                await self.bot.send_message(message.from_user.id, config["bot_unexpected_exception"])
                self._logger.critical(Loggers.APP.value, f"Unexpected error: {exception}.")

    @_private_chat_guard
    @_admin_guard
    async def _handle_remove_user(self, message: types.Message):
        """
        This handler will be called when user sends `/remove_user` command.
        """
        telegram_ids = _parse_command(message)
        if len(telegram_ids) == 0:
            await self.bot.send_message(message.from_user.id, config["user_id_not_specified"])
        for telegram_id in telegram_ids:
            try:
                telegram_id = int(telegram_id)
                if telegram_id < 0:
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Пользователь с id={telegram_id} не добавлен, так как id не может быть отрицательным.",
                    )
                    return
                if not self._db.remove_user(telegram_id):
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Пользователь с id={telegram_id} не удалён, так как он его нет в базе данных.",
                    )
                    return
                await self.bot.send_message(
                    message.from_user.id,
                    f"Пользователь с id={telegram_id} добавлен.",
                )
            except ValueError:
                await self.bot.send_message(message.from_user.id, config["id_contains_more_than_just_numbers"])
            except Exception as exception:  # pylint: disable=W0703
                await self.bot.send_message(message.from_user.id, config["bot_unexpected_exception"])
                self._logger.critical(Loggers.APP.value, f"Unexpected error: {exception}.")

    @_private_chat_guard
    @_admin_guard
    async def _handle_all_user(self, message: types.Message):
        """
        This handler will be called when user sends `/add_user` command.
        """
        try:
            users = self._db.find_all_users()
            users = [str(user_id) for user_id in users]
            await self.bot.send_message(message.from_user.id, "\n".join(users))
        except Exception as exception:  # pylint: disable=W0703
            await self.bot.send_message(message.from_user.id, config["bot_unexpected_exception"])
            self._logger.critical(Loggers.APP.value, f"Unexpected error: {exception}.")

    async def _handle_text(self, message: types.Message):
        """
        This handler will be called when the user sends any text.
        Based on the received question, and answer is generated and sent to the user.
        """
        await self.bot.send_message(message.from_user.id, self._chat_bot.generate_answer(message.text))

    async def _make_a_mailing_list(self, telegram_ids: List[int], message: Message, parse_mode: str):
        """
        A function for sending messages to a specified circle of users.
        @param telegram_ids: id of the users to send the message to.
        @param message: message to be sent
        @param parse_mode: message parsing mode for telegram.
        """
        for telegram_id in telegram_ids:
            try:
                await self.bot.send_message(telegram_id, str(message), parse_mode=parse_mode)
            except ChatNotFound:
                await self.bot.send_message(
                    env_variables["ADMIN_ID_TELEGRAM"],
                    f"Пользователь с id={telegram_id} не существует или не начал чат с ботом.",
                )

    def _register_handlers(self):
        self._dp.register_message_handler(self._handle_start, commands=["start", "about"])
        self._dp.register_message_handler(self._handle_help, commands=["help"])
        self._dp.register_message_handler(self._handle_my_id, commands=["my_id"])
        self._dp.register_message_handler(self._handle_add_user, commands=["add_user"])
        self._dp.register_message_handler(self._handle_remove_user, commands=["remove_user"])
        self._dp.register_message_handler(self._handle_all_user, commands=["all_users"])
        self._dp.register_message_handler(self._handle_text, content_types=["text"])

    async def _check_email_for_messages(self):
        """
        A function that searches for unread messages from the specified user in the environment
        variables and send the contents of the message in a certain format in the telegram.
        """
        self._email_checker.login()
        emails = self._email_checker.get_all_emails_from_inbox()
        emails = self._email_checker.get_unseen_emails(emails)
        emails = self._email_checker.get_emails_by_sender(emails, env_variables["EMAIL_SENDER"])
        emails = self._email_checker.order_emails_by_time(emails)
        for email in emails:
            email.is_read = True
            email.save()
            message_payload = self._email_checker.get_email_message_payloads(email)
            message_subject = self._email_checker.get_email_message_subject(email)
            message_content = Parser.parse_email(message_payload)
            message = Message(message_subject, message_content, is_stylized=True)
            await self._make_a_mailing_list(self._db.find_all_users(), message, parse_mode=types.ParseMode.HTML)
        self._email_checker.logout()

    async def _check_email_for_messages_by_timer(self):
        """
        A function that asynchronously runs the `check_email_for_messages`
        function at some time specified in the environment variables.
        """
        while True:
            await asyncio.sleep(float(env_variables["EMAIL_CHECK_TIME_MIN"]) * 60)
            try:
                await self._check_email_for_messages()
            except EmailCheckerOutlookException as exception:
                message = Message(config["bot_exception"], config["bot_exception_email"], is_stylized=True)
                await self._make_a_mailing_list(self._db.find_all_users(), message, parse_mode=types.ParseMode.HTML)
                self._logger.warning(Loggers.APP.value, f"EmailCheckerOutlookException: {exception}.")
            except ParserException as exception:
                message = Message(config["bot_exception"], config["bot_exception_parser"], is_stylized=True)
                await self._make_a_mailing_list(self._db.find_all_users(), message, parse_mode=types.ParseMode.HTML)
                self._logger.warning(Loggers.APP.value, f"ParserException: {exception}.")
            except MessageException as exception:
                message = Message(config["bot_exception"], config["bot_exception_message"], is_stylized=True)
                await self._make_a_mailing_list(self._db.find_all_users(), message, parse_mode=types.ParseMode.HTML)
                self._logger.warning(Loggers.APP.value, f"MessageException: {exception}.")
            except Exception as exception:  # pylint: disable=W0703
                message = Message(config["bot_exception"], config["bot_unexpected_exception"], is_stylized=True)
                await self._make_a_mailing_list(self._db.find_all_users(), message, parse_mode=types.ParseMode.HTML)
                self._logger.critical(Loggers.APP.value, f"Unexpected error: {exception}.")

    def start(self):
        """
        The main method that starts the `Bot`.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self._check_email_for_messages_by_timer())
        executor.start_polling(self._dp, skip_updates=True)
