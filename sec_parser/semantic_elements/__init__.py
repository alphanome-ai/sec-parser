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
    TableElement,
    TextElement,
    TitleElement,
    TopLevelSectionStartMarker,
    UndeterminedElement,
)

__all__ = [
    "AbstractSemanticElement",
    "AbstractLevelElement",
    "UndeterminedElement",
    "TopLevelSectionStartMarker",
    "TextElement",
    "TitleElement",
    "InvalidLevelError",
    "IrrelevantElement",
    "ImageElement",
    "TableElement",
    "EmptyElement",
    "CompositeSemanticElement",
]
