from __future__ import annotations

import warnings
from abc import ABC, abstractmethod

import bs4
from bs4.builder import XMLParsedAsHTMLWarning

from sec_parser.exceptions import SecParserValueError
from sec_parser.processing_engine.html_tag import HtmlTag

DEFAULT_BEAUTIFUL_SOUP_PARSER_BACKEND = "lxml"


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
        default = DEFAULT_BEAUTIFUL_SOUP_PARSER_BACKEND
        self._parser_backend = (parser_backend or default).lower().strip()

    def parse(self, html: str) -> list[HtmlTag]:
        root: bs4.Tag = self._parse_to_bs4(html)

        elements: list[HtmlTag] = []
        for child in root.children:
            if isinstance(child, bs4.NavigableString) and not child.strip():
                continue
            elements.append(HtmlTag(child))
        if not elements:
            msg = (
                "The HTML document did not contain any top-level tags. "
                "This may indicate that the document is malformed."
            )
            raise SecParserValueError(msg)
        return elements

    def _parse_to_bs4(self, html: str) -> bs4.Tag:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
            root: bs4.Tag = bs4.BeautifulSoup(
                html,
                features=self._parser_backend,
            )
        if root.html:
            root = root.html
            root = root.body if root.body else root
        return root
