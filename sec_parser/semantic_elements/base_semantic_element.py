from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag


class BaseSemanticElement:
    """
    In the domain of HTML parsing, especially in the context of SEC EDGAR documents,
    a semantic element refers to a meaningful unit within the document that serves a
    specific purpose. For example, a paragraph or a table might be considered a
    semantic element. Unlike syntactic elements, which merely exist to structure the
    HTML, semantic elements carry information that is vital to the understanding of the
    document's content.

    This class serves as a foundational representation of such semantic elements,
    containing an HtmlTag object that stores the raw HTML tag information. Subclasses
    will implement additional behaviors based on the type of the semantic element.
    """

    def __init__(
        self: BaseSemanticElement,
        html_tag: HtmlTag,
        inner_elements: list[BaseSemanticElement] | None = None,
    ) -> None:
        self.html_tag = html_tag

        # inner_elements allows for a Semantic Element to act as a container
        # container that can encapsulate other semantic elements.
        # This is used for handling special cases where a single HTML root
        # tag wraps multiple semantic elements. This maintains structural integrity
        # and allows for seamless reconstitution of the original HTML document.
        # Why is this useful:
        # 1. Some semantic elements, like XBRL tags (<ix>), may wrap multiple semantic
        # elements. The container ensures that these relationships are not broken
        # during parsing.
        # 2. Enables the parser to fully reconstruct the original HTML document, which
        # opens up possibilities for features like semantic segmentation visualization
        # (e.g. recreate the original document but put semi-transparent colored boxes
        # on top, based on semantic meaning), serialization of parsed documents into
        # an augmented HTML, and debugging by comparing to the original document.
        self.inner_elements = inner_elements or []

    @classmethod
    def convert_from(
        cls: type[BaseSemanticElement],
        source: BaseSemanticElement,
    ) -> BaseSemanticElement:
        """Convert the semantic element into another semantic element type."""
        return cls(source.html_tag, inner_elements=source.inner_elements)
