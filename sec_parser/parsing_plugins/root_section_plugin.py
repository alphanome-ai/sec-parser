from __future__ import annotations

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.semantic_elements import (
    BaseSemanticElement,
    IrrelevantElement,
    RootSectionElement,
)


class RootSectionPlugin(AbstractElementwiseParsingPlugin):
    """
    RootSectionPlugin class for transforming elements into RootSection instances.

    This plugin scans through a list of semantic elements and replaces
    suitable candidates with RootSection instances.

    Note: We're currently using *sec-api.io* to handle the removal of the
    title 10-Q page and to download 10-Q Section HTML files. The sections
    are then joined by inserting a <document-root-section> separator. In the
    future, we aim to download these HTML files directly from the SEC EDGAR.
    """

    def __init__(self) -> None:
        self.next_element_is_root_section = False

    def transform_element(
        self,
        element: BaseSemanticElement,
        context: ElementwiseParsingContext,
    ) -> BaseSemanticElement:
        if self.next_element_is_root_section:
            self.next_element_is_root_section = False
            return RootSectionElement.convert_from(element)

        if element.html_tag.name == "document-root-section":
            self.next_element_is_root_section = context.is_root
            return IrrelevantElement.convert_from(element)

        if element.html_tag.contains_tag("document-root-section"):
            return RootSectionElement.convert_from(element)

        return element
