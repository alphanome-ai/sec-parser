from __future__ import annotations

from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseFactory(Generic[T]):
    def __init__(
        self,
        cls: type[T],
        **kwargs: dict[str, Any],
    ) -> None:
        self._class = cls
        self._kwargs = kwargs

    def create(self) -> T:
        return self._class(**self._kwargs)
