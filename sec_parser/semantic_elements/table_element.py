from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class TableElement(AbstractSemanticElement):
    """The TableElement class represents a standard table within a document."""

    def get_summary(self) -> str:
        """
        Return a human-readable summary of the semantic element.

        This method aims to provide a simplified, human-friendly representation of
        the underlying HtmlTag.
        """
        return f"{len(self.text)} characters."
