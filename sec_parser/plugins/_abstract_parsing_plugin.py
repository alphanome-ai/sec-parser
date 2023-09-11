from abc import ABC, abstractmethod

from sec_parser.entities._html_tag import HtmlTag


class AbstractParsingPlugin(ABC):
    @abstractmethod
    def apply(self, root_tags: list[HtmlTag]) -> bool:
        raise NotImplementedError
