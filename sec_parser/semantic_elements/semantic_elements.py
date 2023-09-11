from sec_parser.exceptions.core_exceptions import SecParserValueError
from sec_parser.parsing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_elements import (
    AbstractSemanticElement,
)


class UnclaimedElement(AbstractSemanticElement):
    pass


class RootSectionElement(AbstractSemanticElement):
    pass


class TitleElement(AbstractSemanticElement):
    MIN_LEVEL = 1

    def __init__(self, html_tag: HtmlTag, *, level: int = MIN_LEVEL) -> None:
        super().__init__(html_tag)

        if level < self.MIN_LEVEL:
            msg = f"Level must be equal or greater than {self.MIN_LEVEL}"
            raise InvalidTitleLevelError(msg)
        self.level = self.MIN_LEVEL


class TextElement(AbstractSemanticElement):
    pass


class ContentlessElement(AbstractSemanticElement):
    pass


class InvalidTitleLevelError(SecParserValueError):
    pass
