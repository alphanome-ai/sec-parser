from __future__ import annotations

from sec_parser.parsing_plugins.abstract_elementwise_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.semantic_elements import (
    AbstractSemanticElement,
    RootSectionElement,
    RootSectionSeparatorElement,
)


class RootSectionPlugin(AbstractElementwiseParsingPlugin):
    """
    RootSectionPlugin class for transforming elements into RootSection instances.

    This plugin scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with RootSection instances.

    Note: We're currently using *sec-api.io* to handle the removal of the
    title 10-Q page and to download 10-Q Section HTML files. The sections
    are then joined by inserting a <document-root-section> separator. In the
    future, we aim to download these HTML files directly from the SEC EDGAR.
    """

    def __init__(
        self,
        process_only: set[type[AbstractSemanticElement]] | None = None,
        except_dont_process: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            process_only=process_only,
            except_dont_process=except_dont_process,
        )
        self.next_element_is_root_section = False

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        context: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        if context.is_root_element and self.next_element_is_root_section:
            self.next_element_is_root_section = False
            return RootSectionElement.convert_from(element)

        if element.html_tag.name == "document-root-section":
            if context.is_root_element:
                self.next_element_is_root_section = True
            return RootSectionSeparatorElement.convert_from(element)

        contains_root_section = element.html_tag.contains_tag(
            "document-root-section",
            include_self=False,
        )
        if context.is_root_element and contains_root_section:
            return RootSectionElement.convert_from(element)

        return element
