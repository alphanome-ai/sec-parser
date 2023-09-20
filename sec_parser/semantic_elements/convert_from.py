from __future__ import annotations

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractLevelElement,
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.highlighted_element import (
    HighlightedElement,
    TextStyles,
)


def convert_from(
    source: AbstractSemanticElement,
    *,
    to: type[AbstractSemanticElement],
    level: int | None = None,
    styles: TextStyles | None = None,
) -> AbstractSemanticElement:
    cls = to  # for readability
    if issubclass(cls, AbstractLevelElement):
        return cls.convert_from(source, level=level)
    if issubclass(cls, HighlightedElement):
        if styles is None:
            msg = "styles must be specified for HighlightedElement"
            raise ValueError(msg)
        return cls.convert_from(source, styles=styles)
    return cls.convert_from(source)
