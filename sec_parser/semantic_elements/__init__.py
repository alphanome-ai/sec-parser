"""
The semantic_elements subpackage provides abstractions
for meaningful units in SEC EDGAR documents. It converts
raw HTML elements into representations that carry
semantic significance.
"""


from sec_parser.semantic_elements.base_semantic_element import (
    BaseSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    InvalidTitleLevelError,
    IrrelevantElement,
    RootSectionElement,
    TextElement,
    TitleElement,
    UndeterminedElement,
)

__all__ = [
    "BaseSemanticElement",
    "UndeterminedElement",
    "RootSectionElement",
    "TextElement",
    "TitleElement",
    "InvalidTitleLevelError",
    "IrrelevantElement",
]
