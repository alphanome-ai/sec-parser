"""
The processing_engine subpackage contains the core logic
for parsing SEC documents. It is designed to work
in conjunction with the steps from the processing_steps
subpackage to perform tasks like section
identification, title parsing, and text extraction.
"""

from sec_parser.processing_engine.core import (
    AbstractSemanticElementParser,
    Edgar10QParser,
)
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_engine.html_tag_parser import HtmlTagParser

__all__ = [
    "HtmlTagParser",
    "AbstractSemanticElementParser",
    "Edgar10QParser",
    "HtmlTag",
]
