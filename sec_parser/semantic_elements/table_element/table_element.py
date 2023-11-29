from __future__ import annotations

from dataclasses import asdict
from typing import Any

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
        metrics = self.html_tag.get_approx_table_metrics()
        if metrics is None:
            return "Table with {len(self.text)} characters."
        return (
            f"Table with ~{metrics.rows} rows, "
            f"~{metrics.numbers} numbers, and "
            f"{len(self.text)} characters."
        )

    def to_dict(self, include_html_tag: bool | None = None) -> dict[str, Any]:
        metrics = self.html_tag.get_approx_table_metrics()
        return {
            **super().to_dict(include_html_tag),
            "metrics": asdict(metrics) if metrics is not None else None,
        }

    def table_to_markdown(self) -> str:
        return self.html_tag.table_to_markdown()
