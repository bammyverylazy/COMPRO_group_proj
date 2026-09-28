from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Protocol, TypeVar

from ..errors import NotFoundError


class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]:
        ...


T = TypeVar("T", bound=Serializable)


class BaseRepository(ABC, Generic[T]):

    def __init__(self):
        self._items: dict[Any, T] = {}

    @abstractmethod
    def key_of(self, item: T) -> Any:
        pass

    @abstractmethod
    def item_from_dict(self, data: dict[str, Any]) -> T:
        pass

    def get(self, key: Any) -> T:
        if key not in self._items:
            raise NotFoundError(
                f"Item with key {key} not found"
            )

        return self._items[key]

    def find(self, key: Any) -> T | None:
        return self._items.get(key)

    def add(self, item: T) -> T:
        key = self.key_of(item)
        self._items[key] = item
        return item

    def list_all(self) -> list[T]:
        return list(self._items.values())

    def next_id(self) -> int:
        if not self._items:
            return 1

        return max(self._items.keys()) + 1

    def dump(self) -> list[dict[str, Any]]:
        return [
            item.to_dict()
            for item in self._items.values()
        ]

    def load(self, rows: list[dict[str, Any]]) -> None:
        self._items.clear()

        for row in rows:
            item = self.item_from_dict(row)
            self.add(item)