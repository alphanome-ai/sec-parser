from __future__ import annotations

from sec_parser.semantic_elements.abstract_semantic_element import AbstractLevelElement
from sec_parser.semantic_elements.mixins.dict_text_content_mixin import (
    DictTextContentMixin,
)


class TitleElement(DictTextContentMixin, AbstractLevelElement):
    """
    The TitleElement class represents the title of a paragraph or other content object.
    It serves as a semantic marker, providing context and structure to the document.
    """
