"""
The parsing_engine subpackage contains the core logic
for parsing SEC documents. It is designed to work
in conjunction with plugins from the parsing_plugins
subpackage to perform tasks like section
identification, title parsing, and text extraction.
"""

from sec_parser.parsing_engine.abstract_parser import (
    AbstractSemanticElementParser,
)
from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag
from sec_parser.parsing_engine.html_parsers.root_tag_parser import (
    AbstractHtmlTagParser,
    RootTagParser,
)
from sec_parser.parsing_engine.sec_parser import SecParser

__all__ = [
    "AbstractHtmlTagParser",
    "RootTagParser",
    "AbstractSemanticElementParser",
    "SecParser",
    "HtmlTag",
]
