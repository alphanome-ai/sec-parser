from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import ImageElement

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class ImageParsingStep(AbstractElementwiseProcessStep):
    """
    ImageParsingStep class for transforming elements into ImageElement instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with ImageElement instances.
    """

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        is_unary = element.html_tag.is_unary_tree()
        contains_image = element.html_tag.contains_tag("img", include_self=True)
        if is_unary and contains_image:
            return ImageElement.convert_from(element)

        return element
