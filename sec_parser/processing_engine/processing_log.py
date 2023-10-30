import copy
from dataclasses import dataclass
from typing import Any, Union

from loguru import logger

LogItemOrigin = str
LogItemPayload = Union[str, dict[str, Any]]


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
        message: LogItemPayload,
        log_origin: LogItemOrigin,
    ) -> None:
        logger.trace("Adding log item: {}", str(message))
        log_item = LogItem(log_origin, message)
        self._log.append(log_item)

    def get_items(self) -> tuple[LogItem, ...]:
        return tuple(self._log)

    def copy(self) -> "ProcessingLog":
        return copy.deepcopy(self)
