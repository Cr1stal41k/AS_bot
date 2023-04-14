"""
Email checker for outlook module.
"""
from typing import List, Tuple

from exchangelib import DELEGATE, Account, Credentials, Configuration, FaultTolerance
from exchangelib.items.message import Message
from exchangelib.queryset import QuerySet

__all__ = ["EmailCheckerOutlook", "EmailCheckerOutlookException"]


class EmailCheckerOutlookException(Exception):
    """
    Exception class for the `EmailCheckerOutlook`.
    """


class EmailCheckerOutlook:
    """
    Email checker class. Deals with receiving the necessary letters from the mail, for example,
    you can get the title of the letter, its sender, recipient, or contents
    """

    _connection = None
    _email_login = ""
    _email_service_config = None

    def __init__(self, email_host: str, email_login: str, email_password: str, max_wait=100):
        self._email_login = email_login
        email_username = self._email_login.split("@")[0]
        self._email_service_config = Configuration(
            retry_policy=FaultTolerance(max_wait=max_wait),
            server=email_host,
            credentials=Credentials(username=email_username, password=email_password),
        )

    def login(self):
        """
        The method that connects to a outlook mailbox.
        The input parameters are taken from the constructor.
        """
        try:
            self._connection = Account(
                primary_smtp_address=self._email_login,
                autodiscover=False,
                access_type=DELEGATE,
                config=self._email_service_config,
            )
        except Exception as exception:
            raise EmailCheckerOutlookException(f"Unexpected error: {exception}.") from exception

    def logout(self):
        """
        A method that closes an open connection to a outlook mailbox.
        """
        try:
            self._connection.protocol.close()
        except Exception as exception:
            raise EmailCheckerOutlookException(f"Unexpected error: {exception}.") from exception

    def get_all_emails_from_inbox(self) -> QuerySet:
        """
        @return: all messages from the inbox.
        """
        try:
            return self._connection.inbox.all()
        except Exception as exception:
            raise EmailCheckerOutlookException(f"Unexpected error: {exception}.") from exception

    @staticmethod
    def get_unseen_emails(query_set: QuerySet) -> QuerySet:
        """
        @param query_set: a Django QuerySet-like class for querying emails.
        @return: only unread messages from query_set.
        """
        return query_set.filter(is_read=False)

    @staticmethod
    def get_emails_by_sender(query_set: QuerySet, sender: str) -> QuerySet:
        """
        @param query_set: a Django QuerySet-like class for querying emails.
        @param sender: mail of the user from whom the emails came.
        @return: only messages from a specific user from query_set.
        """
        return query_set.filter(sender=sender)

    @staticmethod
    def order_emails_by_time(query_set: QuerySet) -> QuerySet:
        """
        @param query_set: a Django QuerySet-like class for querying emails
        @return: query_set sorted by time.
        """
        return query_set.order_by("-datetime_received")

    @staticmethod
    def get_email_message_sender(email_message: Message) -> Tuple[str, str]:
        """
        Method returning email and sender's name.
        @param email_message: email message object.
        @return: tuple of email and sender's name.
        """
        sender_email = email_message.sender.email_address
        sender_name = email_message.sender.name
        return sender_email, sender_name

    @staticmethod
    def get_email_message_subject(email_message: Message) -> str:
        """
        The method returns the subject of the email message.
        @param email_message: email message object.
        @return: message subject.
        """
        return email_message.subject

    @staticmethod
    def get_email_message_receipt_time(email_message: Message) -> str:
        """
        The method returns the date the email message was sent.
        @param email_message: email message object.
        @return: date the message was sent.
        """
        return email_message.datetime_received

    @staticmethod
    def get_email_message_payloads(email_message: Message) -> str or List[str, str]:
        """
        @param email_message: email message object.
        @return: email payload.
        """
        return email_message.body
