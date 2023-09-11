from sec_parser.entities._abstract_elements import AbstractSemanticElement
from sec_parser.entities._html_tag import HtmlTag
from sec_parser.entities.exceptions import InvalidLevelError


class TitleElement(AbstractSemanticElement):
    MIN_LEVEL = 1

    def __init__(self, html_tag: HtmlTag, *, level: int = MIN_LEVEL) -> None:
        super().__init__(html_tag)

        if level < self.MIN_LEVEL:
            msg = f"Level must be equal or greater than {self.MIN_LEVEL}"
            raise InvalidLevelError(msg)
        self.level = self.MIN_LEVEL
