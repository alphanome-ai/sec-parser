from __future__ import annotations

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractLevelElement,
    AbstractSemanticElement,
)


def convert_from(
    source: AbstractSemanticElement,
    *,
    to: type[AbstractSemanticElement],
    level: int | None = None,
) -> AbstractSemanticElement:
    cls = to  # for readability
    if issubclass(cls, AbstractLevelElement):
        return cls.convert_from(source, level=level)
    return cls.convert_from(source)
