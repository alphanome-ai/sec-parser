"""
The semantic_elements subpackage provides abstractions
for meaningful units in SEC EDGAR documents. It converts
raw HTML elements into representations that carry
semantic significance.
"""


from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractLevelElement,
    AbstractSemanticElement,
    InvalidLevelError,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
    ImageElement,
    IrrelevantElement,
    NotYetClassifiedElement,
    SupplementaryText,
    TextElement,
)
from sec_parser.semantic_elements.table_element import TableElement
from sec_parser.semantic_elements.title_element import TitleElement
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle

__all__ = [
    "AbstractSemanticElement",
    "AbstractLevelElement",
    "NotYetClassifiedElement",
    "TopLevelSectionTitle",
    "TextElement",
    "TitleElement",
    "InvalidLevelError",
    "IrrelevantElement",
    "ImageElement",
    "TableElement",
    "EmptyElement",
    "CompositeSemanticElement",
    "SupplementaryText",
]
