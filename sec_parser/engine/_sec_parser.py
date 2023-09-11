from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.engine._html_parser import AbstractHtmlParser, HtmlParser
from sec_parser.entities._elements import UnclaimedElement
from sec_parser.exceptions._base_exceptions import SecParserRuntimeError
from sec_parser.plugins._plugin_factory import PluginFactory
from sec_parser.plugins._root_section_plugin import RootSectionPlugin
from sec_parser.plugins._text_plugin import TextPlugin
from sec_parser.plugins._title_plugin import TitlePlugin


class MaxIterationsReachedError(SecParserRuntimeError):
    pass


if TYPE_CHECKING:
    from collections.abc import Iterable

    from sec_parser.entities._abstract_elements import AbstractSemanticElement
    from sec_parser.plugins._abstract_parsing_plugin import AbstractParsingPlugin


class SecParser:
    def __init__(
        self,
        *,
        plugins: Iterable[type[AbstractParsingPlugin] | PluginFactory] | None = None,
        html_parser: AbstractHtmlParser | None = None,
        max_iterations: int | None = None,
    ) -> None:
        plugins = plugins or self.get_default_plugins()
        self._plugin_factories = [
            f if isinstance(f, PluginFactory) else PluginFactory(f) for f in plugins
        ]
        self._html_parser = html_parser or HtmlParser()
        self._max_iterations = max_iterations or 10

    def get_default_plugins(self) -> list[type[AbstractParsingPlugin] | PluginFactory]:
        return [RootSectionPlugin, TitlePlugin, TextPlugin]

    def parse(self, html: str) -> list[AbstractSemanticElement]:
        plugins = [factory.create() for factory in self._plugin_factories]
        root_tags = self._html_parser.get_root_tags(html)
        elements: list[AbstractSemanticElement] = [
            UnclaimedElement(tag) for tag in root_tags
        ]

        for _ in range(self._max_iterations):
            modifications: list[bool] = []
            for plugin in plugins:
                modification = plugin.apply(elements)
                modifications.append(modification)
            if not any(modifications):
                break
        else:
            msg = (
                f"Parser could not converge after {self._max_iterations}"
                " iterations, possible infinite loop."
            )
            raise MaxIterationsReachedError(msg)

        return elements
