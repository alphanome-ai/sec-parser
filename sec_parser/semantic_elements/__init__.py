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
from sec_parser.semantic_elements.semantic_elements import (
    BulletpointTextElement,
    EmptyElement,
    FootnoteTextElement,
    ImageElement,
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
    "AbstractLevelElement",
    "UndeterminedElement",
    "RootSectionElement",
    "TextElement",
    "TitleElement",
    "InvalidLevelError",
    "IrrelevantElement",
    "ImageElement",
    "TableElement",
    "RootSectionSeparatorElement",
    "EmptyElement",
    "BulletpointTextElement",
    "FootnoteTextElement",
]
