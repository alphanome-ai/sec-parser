from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag


class AbstractHtmlTagParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> list[HtmlTag]:
        raise NotImplementedError
