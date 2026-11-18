from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class ComponentStatus(StrEnum):
    UP = "up"
    DOWN = "down"


@dataclass(frozen=True)
class HealthReport:
    database: ComponentStatus

    @property
    def is_healthy(self) -> bool:
        return self.database is ComponentStatus.UP


class DatabaseProbe(Protocol):
    """Port: answers whether the database can be reached."""

    def is_available(self) -> bool: ...
