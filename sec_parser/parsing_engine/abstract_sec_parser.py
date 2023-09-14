from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin
    from sec_parser.parsing_plugins.parsing_plugin_factory import ParsingPluginFactory
    from sec_parser.semantic_elements.abstract_semantic_elements import (
        AbstractSemanticElement,
    )


class AbstractSecParser(ABC):
    @abstractmethod
    def __init__(
        self,
        *,
        plugins: Iterable[type[AbstractParsingPlugin] | ParsingPluginFactory]
        | None = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def parse(self, html: str) -> list[AbstractSemanticElement]:
        raise NotImplementedError

    @abstractmethod
    def get_default_plugins(
        self,
    ) -> list[type[AbstractParsingPlugin] | ParsingPluginFactory]:
        raise NotImplementedError
