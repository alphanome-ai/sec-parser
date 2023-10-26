from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

from sec_parser.exceptions import SecParserValueError
from sec_parser.processing_engine.processing_log import LogItemOrigin, ProcessingLog

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_engine.html_tag import HtmlTag


class AbstractSemanticElement(ABC):  # noqa: B024
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
        self,
        html_tag: HtmlTag,
        *,
        processing_log: ProcessingLog | None = None,
        log_origin: LogItemOrigin | None = None,
    ) -> None:
        self._html_tag = html_tag
        self.processing_log = processing_log or ProcessingLog()
        if log_origin:
            self.processing_log.add_item(log_origin=log_origin, message=self)

    @property
    def html_tag(self) -> HtmlTag:
        return self._html_tag

    @classmethod
    def create_from_element(
        cls,
        source: AbstractSemanticElement,
        log_origin: LogItemOrigin,
    ) -> AbstractSemanticElement:
        """Convert the semantic element into another semantic element type."""
        return cls(
            source._html_tag,  # noqa: SLF001
            processing_log=source.processing_log,
            log_origin=log_origin,
        )

    def to_dict(self, include_html_tag: bool | None = None) -> dict[str, Any]:
        result = {"cls_name": self.__class__.__name__}
        if include_html_tag is not False:
            result.update(self._html_tag.to_dict())
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self._html_tag.name}>"

    @property
    def text(self) -> str:
        """Property text is a passthrough to the HtmlTag text property."""
        return self._html_tag.text

    def get_source_code(self, *, pretty: bool = False) -> str:
        """get_source_code is a passthrough to the HtmlTag method."""
        return self._html_tag.get_source_code(pretty=pretty)

    def get_summary(self) -> str:
        """
        Return a human-readable summary of the semantic element.

        This method aims to provide a simplified, human-friendly representation of
        the underlying HtmlTag. In this base implementation, it is a passthrough
        to the HtmlTag's get_text() method.

        Note: Subclasses may override this method to provide a more specific summary
        based on the type of element.
        """
        return self.text


class AbstractLevelElement(AbstractSemanticElement):
    """
    The AbstractLevelElement class provides a level attribute to semantic elements.
    It represents hierarchical levels in the document structure. For instance,
    a main section title might be at level 1, a subsection at level 2, etc.
    """

    MIN_LEVEL = 0

    def __init__(
        self,
        html_tag: HtmlTag,
        *,
        processing_log: ProcessingLog | None = None,
        level: int | None = None,
        log_origin: LogItemOrigin | None = None,
    ) -> None:
        super().__init__(html_tag, processing_log=processing_log, log_origin=log_origin)
        level = level or self.MIN_LEVEL

        if level < self.MIN_LEVEL:
            msg = f"Level must be equal or greater than {self.MIN_LEVEL}"
            raise InvalidLevelError(msg)
        self.level = level

    @classmethod
    def create_from_element(
        cls,
        source: AbstractSemanticElement,
        log_origin: LogItemOrigin,
        *,
        level: int | None = None,
    ) -> AbstractLevelElement:
        return cls(
            source._html_tag,  # noqa: SLF001
            processing_log=source.processing_log,
            level=level,
            log_origin=log_origin,
        )

    def to_dict(self, include_html_tag: bool | None = None) -> dict[str, Any]:
        return {
            **super().to_dict(include_html_tag),
            "level": self.level,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[L{self.level}]<{self._html_tag.name}>"


class InvalidLevelError(SecParserValueError):
    pass
