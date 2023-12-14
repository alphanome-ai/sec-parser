from typing import Any

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class DictTextContentMixin(AbstractSemanticElement):
    def to_dict(
        self,
        *,
        include_previews: bool = False,
        include_contents: bool = False,
    ) -> dict[str, Any]:
        result = super().to_dict(
            include_previews=include_previews,
            include_contents=include_contents,
        )
        if include_contents:
            result["text_content"] = self.text
        return result
