from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.exceptions.core_exceptions import SecParserRuntimeError
from sec_parser.parsing_engine.abstract_sec_parser import AbstractSecParser
from sec_parser.parsing_engine.root_tag_parser import (
    AbstractRootTagParser,
    RootTagParser,
)
from sec_parser.parsing_plugins.contentless_plugin import ContentlessPlugin
from sec_parser.parsing_plugins.parsing_plugin_factory import ParsingPluginFactory
from sec_parser.parsing_plugins.root_section_plugin import RootSectionPlugin
from sec_parser.parsing_plugins.text_plugin import TextPlugin
from sec_parser.parsing_plugins.title_plugin import TitlePlugin
from sec_parser.semantic_elements.semantic_elements import (
    UnclaimedElement,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin
    from sec_parser.semantic_elements.abstract_semantic_elements import (
        AbstractSemanticElement,
    )


class MaxIterationsReachedError(SecParserRuntimeError):
    pass


class SecParser(AbstractSecParser):
    def __init__(
        self,
        *,
        plugins: Iterable[type[AbstractParsingPlugin] | ParsingPluginFactory]
        | None = None,
        root_tag_parser: AbstractRootTagParser | None = None,
        max_iterations: int | None = None,
    ) -> None:
        plugins = plugins or self.get_default_plugins()
        self._plugin_factories = [
            f if isinstance(f, ParsingPluginFactory) else ParsingPluginFactory(f)
            for f in plugins
        ]
        self._root_tag_parser = root_tag_parser or RootTagParser()
        self._max_iterations = max_iterations or 10

    def get_default_plugins(
        self,
    ) -> list[type[AbstractParsingPlugin] | ParsingPluginFactory]:
        return [RootSectionPlugin, TitlePlugin, TextPlugin, ContentlessPlugin]

    def parse(self, html: str) -> list[AbstractSemanticElement]:
        plugins = [factory.create() for factory in self._plugin_factories]
        root_tags = self._root_tag_parser.parse(html)

        elements: list[AbstractSemanticElement] = [
            UnclaimedElement(tag) for tag in root_tags
        ]

        for _ in range(self._max_iterations):
            modified = False
            for plugin in plugins:
                # Caution: The "elements" list can be modified
                # in-place without any safeguards in the plugin.
                # This is intentional to allow for more efficient parsing.
                result = plugin.apply(elements)
                if result is not None:
                    modified = True
                    elements = result
            if not modified:
                break
        else:
            msg = (
                f"Parser could not converge after {self._max_iterations}"
                " iterations, possible infinite loop."
            )
            raise MaxIterationsReachedError(msg)

        return elements
