from __future__ import annotations

import warnings

import bs4

from sec_parser.parsing_engine.html_parsers.abstract_html_tag_parser import (
    AbstractHtmlTagParser,
)
from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag


class RootTagParser(AbstractHtmlTagParser):
    def __init__(self, parser_backend: str | None = None) -> None:
        self._parser_backend = (parser_backend or "lxml").lower().strip()

    def parse(self, html: str) -> list[HtmlTag]:
        soup = bs4.BeautifulSoup(html, self._parser_backend)
        if soup.body is None:
            return []

        elements = []
        for child in soup.body.children:
            if isinstance(child, bs4.Tag):
                elements.append(HtmlTag(child))
            elif isinstance(child, bs4.NavigableString):
                if not child.strip():
                    continue
                new_child = soup.new_tag("span")
                new_child.string = str(child)
                msg = "NavigableString found in body. Converting to span."
                warnings.warn(msg, stacklevel=2)
                elements.append(HtmlTag(new_child))
            else:
                msg = f"Unsupported element type {type(child)} found in body."
                warnings.warn(msg, stacklevel=2)
        return elements
