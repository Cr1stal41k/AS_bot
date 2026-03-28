from src.core.config import all_email_subjects


def is_email_not_in_configs(message_subject: str) -> bool:
    for email_subject in all_email_subjects:
        if email_subject in message_subject:
            return False
    return True
