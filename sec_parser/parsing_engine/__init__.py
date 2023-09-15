"""
The parsing_engine subpackage contains the core logic
for parsing SEC documents. It is designed to work
in conjunction with plugins from the parsing_plugins
subpackage to perform tasks like section
identification, title parsing, and text extraction.
"""

from sec_parser.parsing_engine.abstract_sec_parser import AbstractSecParser
from sec_parser.parsing_engine.html_tag import HtmlTag
from sec_parser.parsing_engine.root_tag_parser import (
    AbstractRootTagParser,
    RootTagParser,
)

__all__ = [
    "AbstractRootTagParser",
    "RootTagParser",
    "AbstractSecParser",
    "SecParser",
    "HtmlTag",
]
