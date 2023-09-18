"""
The semantic_elements subpackage provides abstractions
for meaningful units in SEC EDGAR documents. It converts
raw HTML elements into representations that carry
semantic significance.
"""


from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    HighlightedElement,
    ImageElement,
    InvalidTitleLevelError,
    IrrelevantElement,
    RootSectionElement,
    RootSectionSeparatorElement,
    TableElement,
    TextElement,
    TitleElement,
    UndeterminedElement,
)

__all__ = [
    "AbstractSemanticElement",
    "UndeterminedElement",
    "RootSectionElement",
    "TextElement",
    "TitleElement",
    "InvalidTitleLevelError",
    "IrrelevantElement",
    "ImageElement",
    "TableElement",
    "RootSectionSeparatorElement",
    "HighlightedElement",
]
