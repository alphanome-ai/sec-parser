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

        # If creating derived classes that override __init__, make sure to call this
        # at the very end the derived class's __init__ method. Pass log_origin=None to
        # the base class. This is to ensure that the log_init is called at the very end
        # of the __init__
        self.log_init(log_origin)

    def log_init(self, log_origin: LogItemOrigin | None = None) -> None:
        """Has to be called at the very end of the __init__ method."""
        if log_origin:
            self.processing_log.add_item(
                log_origin=log_origin,
                message=self.to_dict(include_previews=False),
            )

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

    def to_dict(
        self,
        *,
        include_previews: bool = False,
        include_contents: bool = False,
    ) -> dict[str, Any]:
        _ = include_contents

        result = {"cls_name": self.__class__.__name__}
        if include_previews is not False:
            result.update(self._html_tag.to_dict())
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self._html_tag.name}>"

    def contains_words(self) -> bool:
        """Return True if the semantic element contains text."""
        return self._html_tag.contains_words()

    @property
    def text(self) -> str:
        """Property text is a passthrough to the HtmlTag text property."""
        return self._html_tag.text

    def get_source_code(
        self,
        *,
        pretty: bool = False,
        enable_compatibility: bool = False,
    ) -> str:
        """get_source_code is a passthrough to the HtmlTag method."""
        return self._html_tag.get_source_code(
            pretty=pretty,
            enable_compatibility=enable_compatibility,
        )

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
        super().__init__(html_tag, processing_log=processing_log, log_origin=None)
        level = level or self.MIN_LEVEL

        if level < self.MIN_LEVEL:
            msg = f"Level must be equal or greater than {self.MIN_LEVEL}"
            raise InvalidLevelError(msg)
        self.level = level
        self.log_init(log_origin)  # Has to be called at the very end

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

    def to_dict(
        self,
        *,
        include_previews: bool = False,
        include_contents: bool = False,
    ) -> dict[str, Any]:
        return {
            **super().to_dict(
                include_previews=include_previews,
                include_contents=include_contents,
            ),
            "level": self.level,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[L{self.level}]<{self._html_tag.name}>"


class InvalidLevelError(SecParserValueError):
    pass
