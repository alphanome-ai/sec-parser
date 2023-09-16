from __future__ import annotations

import bs4

from sec_parser.parsing_engine.html_parsers.abstract_html_tag_parser import (
    AbstractHtmlTagParser,
)
from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag


class RootTagParser(AbstractHtmlTagParser):
    """
    RootTagParser is a class designed to handle the primarily
    flat HTML structure of SEC filings.
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
