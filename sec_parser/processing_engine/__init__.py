"""
The processing_engine subpackage contains the core logic
for parsing SEC documents. It is designed to work
in conjunction with the steps from the processing_steps
subpackage to perform tasks like section
identification, title parsing, and text extraction.
"""

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_engine.html_tag_parser import HtmlTagParser
from sec_parser.processing_engine.sec_parser import (
    AbstractSemanticElementParser,
    SecParser,
)

__all__ = [
    "HtmlTagParser",
    "AbstractSemanticElementParser",
    "SecParser",
    "HtmlTag",
]
