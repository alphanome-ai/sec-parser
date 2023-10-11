from __future__ import annotations

from abc import ABC, abstractmethod

import bs4

from sec_parser.processing_engine.html_tag import HtmlTag


class AbstractHtmlTagParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> list[HtmlTag]:
        raise NotImplementedError  # pragma: no cover


class HtmlTagParser(AbstractHtmlTagParser):
    """
    The HtmlTagParser parses an HTML document using BeautifulSoup4.
    It then wraps the parsed bs4.Tag objects into HtmlTag objects.
    """

    def __init__(self, parser_backend: str | None = None) -> None:
        self._parser_backend = (parser_backend or "lxml").lower().strip()

    def parse(self, html: str) -> list[HtmlTag]:
        soup = bs4.BeautifulSoup(html, self._parser_backend)
        if soup.body is None:
            return []

        elements = []
        for child in soup.body.children:
            if isinstance(child, bs4.NavigableString) and not child.strip():
                continue
            elements.append(HtmlTag(child))
        return elements
