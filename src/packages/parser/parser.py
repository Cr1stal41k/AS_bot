"""
Parsing module.
"""
from typing import Tuple, List
from bs4 import BeautifulSoup

__all__ = ["Parser", "ParserException"]


class ParserException(Exception):
    """
    Exception class for the `Parser`.
    """


class Parser:
    """
    Parser class. He is engaged in parsing various html structures,
    for example, the contents of a letter in html format.
    """

    @staticmethod
    def _remove_garbage(text: str) -> str:
        text = text.strip()
        text = text.replace("  ", "")
        text = text.replace("\n", "")
        text = text.replace("\r", "")
        return text

    @classmethod
    def _parse_table_1(cls, soup: BeautifulSoup) -> Tuple[List[str], List[List[str]]]:
        message_heading_of_table = soup.body.find_all("th")
        message_heading_of_table = [cls._remove_garbage(i.text) for i in message_heading_of_table]

        message_content_of_table = soup.body.find_all("td")
        message_content_of_table = [cls._remove_garbage(i.text) for i in message_content_of_table]
        return message_heading_of_table, [message_content_of_table]

    @classmethod
    def _parse_table_2(cls, soup: BeautifulSoup) -> Tuple[List[str], List[List[str]]]:
        message_heading_of_table = soup.body.find("thead")
        message_heading_of_table = message_heading_of_table.tr.find_all("td")
        message_heading_of_table = [cls._remove_garbage(i.text) for i in message_heading_of_table]

        t_body = soup.body.find("tbody")
        message_content_of_table = cls._parse_table_body(t_body)
        return message_heading_of_table, message_content_of_table

    @classmethod
    def _parse_table_3(cls, soup: BeautifulSoup) -> Tuple[List[str], List[List[str]]]:
        t_body = soup.body.find("tbody")
        message_content_of_table = cls._parse_table_body(t_body)
        message_heading_of_table = message_content_of_table.pop(0)
        return message_heading_of_table, message_content_of_table

    @classmethod
    def _parse_table_body(cls, t_body: BeautifulSoup) -> List[List[str]]:
        message_content_of_table = []
        for table_r in t_body.find_all("tr"):
            texts = []
            for table_d in table_r.find_all("td"):
                text = cls._remove_garbage(table_d.text)
                if not text:
                    continue
                texts.append(text)
            if not texts:
                continue
            message_content_of_table.append(texts)
        return message_content_of_table

    @classmethod
    def _parse_text(cls, soup: BeautifulSoup) -> str:
        return cls._remove_garbage(soup.text)

    @classmethod
    def parse_email(cls, message_payload_html) -> Tuple[List[str], List[List[str]]] or str:
        """
        Method for parsing a message containing a single table.
        We get a list of table headers and a list of table contents.
        @param message_payload_html: message contents in html format.
        @return: list of table headers and a list of table contents.
        """
        soup = BeautifulSoup(message_payload_html, "lxml")
        res = soup.text
        t = res.split('\n')
        new_text = ''
        for i in t:
            if i != '' and i != '\xa0':
                new_text = new_text + '\n' + i
        return new_text
        # if soup.body.find_all("th"):
        #     return cls._parse_table_1(soup)
        # if soup.body.find_all("thead"):
        #     return cls._parse_table_2(soup)
        # if soup.body.find_all("tbody"):
        #     return cls._parse_table_3(soup)
        # return cls._parse_text(soup)
