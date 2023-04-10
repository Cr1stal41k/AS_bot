"""
Email checker module.
"""
from imaplib import IMAP4_SSL
import email
from email.message import Message
from email.header import decode_header
from typing import List, Tuple

__all__ = ["EmailChecker", "EmailCheckerException"]


class EmailCheckerException(Exception):
    """
    Exception class for the `EmailChecker`.
    """


class EmailChecker:
    """
    Email checker class. Deals with receiving the necessary letters from the mail, for example,
    you can get the title of the letter, its sender, recipient, or contents
    """

    _imap4_ssl = None
    _email_host: str
    _email_login: str
    _email_password: str
    _email_port: int

    def __init__(self, email_host: str, email_login: str, email_password: str, email_port=0):
        self._email_host = email_host
        self._email_login = email_login
        self._email_password = email_password
        self._email_port = email_port

    def login(self):
        """
        A method that logs into an email account over an ssl connection.
        The input parameters are taken from the constructor.
        """
        try:
            self._imap4_ssl = (
                IMAP4_SSL(self._email_host, self._email_port) if self._email_port else IMAP4_SSL(self._email_host)
            )
            self._imap4_ssl.login(self._email_login, self._email_password)
            status, _ = self._imap4_ssl.select("INBOX")
            if status != "OK":
                raise EmailCheckerException("Request status failed.")
        except Exception as exception:
            raise EmailCheckerException(f"Unexpected error: {exception}.") from exception

    def logout(self):
        """
        A method that closes an open ssl connection to a mail account.
        """
        try:
            self._imap4_ssl.close()
            self._imap4_ssl.logout()
        except Exception as exception:
            raise EmailCheckerException(f"Unexpected error: {exception}.") from exception

    def get_unseen_emails(self) -> List[bytes]:
        """
        Method for getting all unseen messages.
        @return: list of id's of all unread messages in byte format.
        """
        try:
            status, unseen_emails_id = self._imap4_ssl.search(None, "UNSEEN")
            if status != "OK":
                raise EmailCheckerException("Request status failed.")
            unseen_emails_id = unseen_emails_id[0].split()
            return unseen_emails_id
        except Exception as exception:
            raise EmailCheckerException(f"Unexpected error: {exception}.") from exception

    def read_email_message(self, email_id_bytes: bytes) -> Message:
        """
        A method that sends a request by id to receive a letter using the protocol (RFC822).
        @param email_id_bytes: email id in byte format.
        @return: email message object.
        """
        try:
            status, data_email = self._imap4_ssl.fetch(email_id_bytes, "(RFC822)")
            if status != "OK":
                raise EmailCheckerException("Request status failed.")
            raw_email = data_email[0][1]
            email_message = email.message_from_bytes(raw_email)
            return email_message
        except Exception as exception:
            raise EmailCheckerException(f"Unexpected error: {exception}.") from exception

    @staticmethod
    def get_email_message_sender(email_message: Message) -> Tuple[str, str]:
        """
        Method returning email and sender's name.
        @param email_message: email message object.
        @return: tuple of email and sender's name.
        """
        try:
            sender_name_bytes, sender_email = email.utils.parseaddr(email_message["From"])
            sender_name_encoded, encoding = decode_header(sender_name_bytes)[0]
            sender_name = sender_name_encoded.decode(encoding)
            return sender_email, sender_name
        except Exception as exception:
            raise EmailCheckerException(f"Unexpected error: {exception}.") from exception

    @staticmethod
    def get_email_message_subject(email_message: Message) -> str:
        """
        The method returns the subject of the email message.
        @param email_message: email message object.
        @return: decoded message subject.
        """
        message_subject = email_message["Subject"]
        message_subject_encoded, encoding = decode_header(message_subject)[0]
        message_subject = message_subject_encoded.decode(encoding)
        return message_subject

    @staticmethod
    def get_email_message_receipt_time(email_message: Message) -> str:
        """
        The method returns the date the email message was sent.
        @param email_message: email message object.
        @return: date the message was sent.
        """
        return email_message["Date"]

    @staticmethod
    def get_email_message_payloads(email_message: Message) -> str or List[str, str]:
        """
        Method that returns the contents of the email. If the email message is not a multipart,
        then an array containing one element is returned - the decoded contents of the letter.
        Otherwise, an array is returned with the decoded contents and the contents in html format.
        @param email_message: email message object.
        @return: email payload.
        """
        try:
            payloads = []
            if email_message.is_multipart():
                for payload in email_message.get_payload():
                    body = payload.get_payload(decode=True).decode("utf-8")
                    payloads.append(body)
            else:
                body = email_message.get_payload(decode=True).decode("utf-8")
                payloads.append(body)
            return payloads
        except Exception as exception:
            raise EmailCheckerException(f"Unexpected error: {exception}.") from exception
