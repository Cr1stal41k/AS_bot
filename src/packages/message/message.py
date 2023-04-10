"""
Message module.
"""
from typing import List, Tuple
import aiogram.utils.markdown as fmt

__all__ = ["Message", "MessageException"]


class MessageException(Exception):
    """
    Exception class for the `Message`.
    """


class Message:
    """
    Class of `Message`. Objects of this class are specific template messages
    that have a header, content and, in the future, attached files.
    """

    title: str
    content: str
    _headings: List[str]
    _contents: List[List[str]]
    _heading_and_content: List[str]
    is_stylized: bool
    files: None

    def __init__(self, title: str, content: Tuple[List[str], List[List[str]]] or str, is_stylized=False):
        self.title = title
        self.is_stylized = is_stylized
        if isinstance(content, str):
            self.content = content
            return
        headings = content[0]
        contents = content[1]
        for cont in contents:
            if len(headings) != len(cont):
                raise MessageException("Heading and contents length are not equal.")
        self._headings = headings
        self._contents = contents
        self._heading_and_content = self._to_str_headings_and_contents()
        self.content = "\n".join(self._heading_and_content)

    def __str__(self):
        if self.is_stylized:
            return fmt.text(
                fmt.text(fmt.hunderline(self.title)),
                fmt.text(),
                self.content,
                sep="\n",
            )
        return f"{self.title}\n" f"\n" + self.content

    def _to_str_headings_and_contents(self) -> List[str]:
        heading_and_content = []
        for content in self._contents:
            for head, cont in zip(self._headings, content):
                heading_and_content.append(self._to_str_heading_and_content(head, cont))
        return heading_and_content

    def _to_str_heading_and_content(self, heading, content) -> str:
        if self.is_stylized:
            return fmt.text(fmt.hbold(heading), ": ", content)
        return f"{heading}: {content}"
