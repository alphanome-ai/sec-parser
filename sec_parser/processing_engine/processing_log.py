import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


LogItemOrigin = str
LogItemPayload = Union[str, "AbstractSemanticElement"]


@dataclass(frozen=True)
class LogItem:
    origin: LogItemOrigin
    payload: LogItemPayload


class ProcessingLog:
    def __init__(self) -> None:
        self._log: list[LogItem] = []

    def add_item(
        self,
        *,
        log_origin: LogItemOrigin,
        message: LogItemPayload,
    ) -> None:
        log_item = LogItem(log_origin, message)
        self._log.append(log_item)

    def get_items(self) -> tuple[LogItem, ...]:
        return tuple(self._log)

    def copy(self) -> "ProcessingLog":
        return copy.deepcopy(self)
