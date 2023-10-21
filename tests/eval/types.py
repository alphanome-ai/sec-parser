from dataclasses import dataclass
from typing import List

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from tests._sec_parser_validation_data import Report


@dataclass
class ParsedDocumentComponents:
    report: Report
    html_tags: list[HtmlTag]
    semantic_elements: list[AbstractSemanticElement]
