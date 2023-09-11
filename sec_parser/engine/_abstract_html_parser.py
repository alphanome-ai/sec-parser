from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.entities._html_tag import HtmlTag


class AbstractHtmlParser(ABC):
    @abstractmethod
    def get_root_tags(self, html: str) -> list[HtmlTag]:
        raise NotImplementedError
