from __future__ import annotations

from typing import Any, Generic, TypeVar

from sec_parser.plugins._abstract_parsing_plugin import AbstractParsingPlugin

T = TypeVar("T", bound=AbstractParsingPlugin)


class PluginFactory(Generic[T]):
    def __init__(
        self,
        plugin_class: type[T],
        **kwargs: dict[str, Any],
    ) -> None:
        self._plugin_class = plugin_class
        self._kwargs = kwargs

    def create(self) -> T:
        return self._plugin_class(**self._kwargs)
