import sys
from collections.abc import (
    Iterator,
    Iterable,
    Callable,
    Mapping,
    MutableMapping,
    ItemsView,
    ValuesView,
    KeysView,
)
from typing import Any, overload, Optional, TypeVar, Union

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


K = TypeVar("K")
V = TypeVar("V")


class _IndexedDictKeysView(KeysView[K]):
    def __init__(self, indexed_dict: "IndexedDict[K, V]"):
        self._indexed_dict = indexed_dict

    def __contains__(self, key: object) -> bool:
        return key in self._indexed_dict._dict

    def __iter__(self) -> Iterator[K]:
        return iter(self._indexed_dict._index)

    def __len__(self) -> int:
        return len(self._indexed_dict._index)


class _IndexedDictValuesView(ValuesView[V]):
    def __init__(self, indexed_dict: "IndexedDict[K, V]"):
        self._indexed_dict = indexed_dict

    def __contains__(self, value: object) -> bool:
        for k in self._indexed_dict._index:
            if self._indexed_dict._dict[k].value == value:
                return True
        return False

    def __iter__(self) -> Iterator[V]:
        for k in self._indexed_dict._index:
            yield self._indexed_dict._dict[k].value

    def __len__(self) -> int:
        return len(self._indexed_dict._index)


class _IndexedDictItemsView(ItemsView[K, V]):
    def __init__(self, indexed_dict: "IndexedDict[K, V]"):
        self._indexed_dict = indexed_dict

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, tuple) or len(item) != 2:
            return False
        key, value = item
        return (
            key in self._indexed_dict._dict
            and self._indexed_dict._dict[key].value == value
        )

    def __iter__(self) -> Iterator[tuple[K, V]]:
        for k in self._indexed_dict._index:
            yield (k, self._indexed_dict._dict[k].value)

    def __len__(self) -> int:
        return len(self._indexed_dict._index)


class _Node:
    __slots__ = ("value", "index")

    def __init__(self, value: V, index: int):
        self.value = value
        self.index = index

    def __repr__(self):
        return f"_Node({self.value}, {self.index})"

    def __str__(self):
        return f"({self.value}, {self.index})"

    def __eq__(self, other):
        return self.value == other.value and self.index == other.index


class IndexedDict(MutableMapping[K, V]):
    """
    A dictionary that preserves insertion order and allows index-based operations.

    In addition to all the usual dict methods (key lookup, iteration, membership,
    pop, update, etc.), you can also:

        - Access by integer index:         `d.get_from_index(i)` or `d[i]` if
            you slice.
        - Get the key at a given index:    `d.get_key_from_index(i)`.
        - Remove by index:                 `d.pop_from_index(i)` or `del d[i:j]`.
        - Insert at an arbitrary position: `d.insert(idx, key, value)`.
        - Move an existing key:            `d.move_to_index(key, new_idx)`.
        - Slice the dict in order:         `d[1:4]`, `del d[2:5]`,
            `d[0:3] = […]`.
        - Sort by key or custom function:  `d.sort()` or
            `d.sort(key=…, reverse=…)`.
        - Export back to a plain dict:     `d.to_dict()`.

    Internally, self._index holds the keys in insertion (or user-reordered)
    order and self._dict maps keys → values for O(1) lookup.
    """

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, data: Mapping[K, V]) -> None: ...
    @overload
    def __init__(self, data: Mapping[K, V], **kwargs: V) -> None: ...
    @overload
    def __init__(self, data: Iterable[tuple[K, V]]) -> None: ...
    @overload
    def __init__(self, data: Iterable[tuple[K, V]], **kwargs: V) -> None: ...
    @overload
    def __init__(self, data: None = None, **kwargs: V) -> None: ...
    def __init__(
        self,
        data: Mapping[K, V] | Iterable[tuple[K, V]] | None = None,
        **kwargs: V,
    ) -> None:
        """
        Initialize an IndexedDict.

        Args:
            data (Mapping[K, V] | Iterable[tuple[K, V]] | None, optional): Initial data.
                Defaults to None.
            **kwargs (V): Additional key-value pairs to add to the IndexedDict.
        """
        self._index: list[K] = []
        self._dict: dict[K, _Node] = {}
        data = data or {}
        self._add_data(self, data, **kwargs)

    def __setitem__(
        self, key_or_slice: Union[K, slice], value: Union[V, Iterable[V]]
    ) -> None:
        """
        Assign value(s).

        - If key_or_slice is a single key, behave like dict: insert or replace.
        - If key_or_slice is a slice, value must be an iterable of new values;
          replaces the values at those positions without changing keys.
        """
        if isinstance(key_or_slice, slice):
            keys = self._index[key_or_slice]
            if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
                raise TypeError(
                    "Slice assignment requires a non-string iterable of values"
                )
            vals = list(value)
            if len(vals) != len(keys):
                raise ValueError("Slice assignment length mismatch")
            for k, v in zip(keys, vals):
                self._dict[k].value = v
        elif key_or_slice in self._dict:
            self._dict[key_or_slice].value = value
        else:
            self._index.append(key_or_slice)
            self._dict[key_or_slice] = _Node(value, len(self._index) - 1)

    def __getitem__(self, key_or_slice: Union[K, slice]) -> Any:
        """
        Retrieve item(s).

        - If key_or_slice is a key, return its value.
        - If key_or_slice is a slice, return a list of values in that index range.
        """
        if isinstance(key_or_slice, slice):
            return [self._dict[k].value for k in self._index[key_or_slice]]
        return self._dict[key_or_slice].value

    def __delitem__(self, key_or_slice: Union[K, slice]) -> None:
        """
        Delete entry(ies).

        - If key_or_slice is a key, remove that key and its value.
        - If key_or_slice is a slice, remove all keys in that index range.
        """
        if isinstance(key_or_slice, slice):
            for k in self._index[key_or_slice]:
                del self._dict[k]
            del self._index[key_or_slice]
            start_index = key_or_slice.start if key_or_slice.start is not None else 0
            self._resync_indices(start=start_index)
        else:
            if key_or_slice not in self._dict:
                raise KeyError(key_or_slice)
            self._index.remove(key_or_slice)
            removed = self._dict.pop(key_or_slice)
            self._resync_indices(start=removed.index)

    def __eq__(self, other: object) -> bool:
        """Test for equality."""
        if isinstance(other, IndexedDict):
            return list(self.items()) == list(other.items())
        return self.to_dict() == dict(other) if isinstance(other, Mapping) else False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __or__(self, other: Mapping[K, V]) -> Self:
        new = self.copy()
        new.update(other)
        return new

    def __ior__(self, other: Mapping[K, V]) -> Self:
        self.update(other)
        return self

    def __len__(self) -> int:
        """Return number of entries."""
        return len(self._index)

    def __iter__(self) -> Iterator[K]:
        """Yield keys in their current order."""
        return iter(self._index)

    def __repr__(self) -> str:
        items = ", ".join(f"{k!r}: {self._dict[k]!r}" for k in self._index)
        return f"{self.__class__.__name__}({{{items}}})"

    def __str__(self) -> str:
        return str({k: self._dict[k].value for k in self._index})

    def __contains__(self, key: object) -> bool:
        """Tests membership in the dict."""
        return key in self._dict

    def __bool__(self) -> bool:
        """Checks if dict is non-empty."""
        return bool(self._dict)

    def __reversed__(self) -> Iterator[K]:
        """Iterates keys in reverse order."""
        return reversed(self._index)

    def __copy__(self) -> Self:
        return self.copy()

    # ——— Private Methods ———
    @staticmethod
    def _add_data(
        _obj: Self,
        _data: Union[Mapping[K, V], Iterable[tuple[K, V]]],
        **kwargs: V,
    ) -> None:
        """Add data to an existing or new IndexedDict."""

        def _add_data_to_obj(data):
            for k, v in data:
                if k in _obj._dict:
                    _obj._dict[k].value = v
                else:
                    _obj._index.append(k)
                    _obj._dict[k] = _Node(v, len(_obj._index) - 1)

        if isinstance(_data, Mapping):
            _add_data_to_obj(_data.items())
        elif isinstance(_data, Iterable):
            _add_data_to_obj(_data)
        elif _data is not None:
            raise TypeError("_data must be a mapping or iterable of (key, value) pairs")
        _add_data_to_obj(kwargs.items())

    def _resync_indices(self, start: int = 0) -> None:
        """After any operation shifting tail of _order, rewrite node.index."""
        for index in range(start, len(self._index)):
            key = self._index[index]
            self._dict[key].index = index

    # ——— Public Methods ———
    def position(self, key: K) -> int:
        """Return the position index of a key.

        Returns index of key.

        Raises ValueError if the key is not found.
        """
        if key not in self._dict:
            raise ValueError(f"Key '{key}' not found in IndexedDict")
        return self._dict[key].index

    def get_from_index(self, index: int) -> V:
        """Return the value at a given insertion-index.

        Returns value at index.

        Raises IndexError if out of range.
        """
        return self._dict[self._index[index]].value

    def get_key_from_index(self, index: int) -> K:
        """Return the key at a given insertion-index.

        Returns key at index.

        Raises IndexError if out of range.
        """
        return self._index[index]

    def pop_from_index(self, index: int) -> V:
        """Remove and return the value at a given index.

        Shifts subsequent items left.

        Returns value at index.
        """
        key = self._index.pop(index)
        return self._dict.pop(key).value

    def to_dict(self) -> dict[K, V]:
        """Export to a plain built-in dict, preserving current order.

        Returns: dict of {key: value}
        """
        return {key: self._dict[key].value for key in self._index}

    # ——— List-like Methods ———
    def insert(self, index: int, key: K, value: V) -> None:
        """Insert a new key/value at the given index.

        Shifts subsequent items to the right.

        Raises KeyError if key already present.
        """
        if key in self._dict:
            raise KeyError("insert(): key already present")

        if index < 0:
            index = max(0, len(self._index) + index)

        index = min(index, len(self._index))
        self._index.insert(index, key)
        self._dict[key] = _Node(value, index)
        self._resync_indices(start=index + 1)

    def move_to_index(self, key: K, new_index: int) -> None:
        """Relocate an existing key to a new index position.

        Raises KeyError if key is not present.
        """
        if key not in self._dict:
            raise KeyError(key)

        node = self._dict[key]
        old_index = node.index
        self._index.remove(key)

        if new_index < 0:
            new_index = max(0, len(self._index) + new_index + 1)
        else:
            new_index = min(new_index, len(self._index))

        self._index.insert(new_index, key)
        node.index = new_index
        self._resync_indices(start=min(old_index, new_index))

    def sort(
        self,
        *,
        key: Optional[Callable[[K], Any]] = None,
        reverse: bool = False,
    ) -> None:
        """Sort keys in-place.

        Args:
            key: optional function mapping a key → comparison key. If None,
                sorts by key.
            reverse: if True, reverse the sort order.
        """
        self._index.sort(key=key, reverse=reverse)  # type: ignore
        self._resync_indices()

    # ——— Standard‐API Methods (dict‐like) ———

    def keys(self) -> KeysView[K]:
        """Return a view of keys."""
        return _IndexedDictKeysView(self)

    def values(self) -> ValuesView[V]:
        """Return a view of values."""
        return _IndexedDictValuesView(self)

    def items(self) -> ItemsView[K, V]:
        """Return a view of key/value pairs."""
        return _IndexedDictItemsView(self)

    def clear(self) -> None:
        """Remove all items."""
        self._index.clear()
        self._dict.clear()

    def copy(self) -> Self:
        """Return a shallow copy of the IndexedDict."""
        new = self.__class__()
        new._index = self._index.copy()
        new._dict = self._dict.copy()
        return new

    def pop(self, key: K, default: Any = ...) -> V:
        """Remove specified key and return its value.

        Return default if not found and default is provided.

        Raise KeyError if key not found and default not provided.
        """
        if key in self._dict:
            self._index.remove(key)
            return self._dict.pop(key).value
        if default is not ...:
            return default
        raise KeyError(key)

    def popitem(self) -> tuple[K, V]:
        """Remove and return the last key/value pair.

        Returns (key, value).

        Raises KeyError if empty.
        """
        if not self._index:
            raise KeyError("popitem(): dictionary is empty")
        key = self._index.pop()
        return key, self._dict.pop(key).value

    def setdefault(self, key: K, default: Optional[V] = None) -> V:
        """Implement setdefault().

        If key in dict: return its value.
        Else: insert key with default and return default.
        """
        if key not in self._dict:
            self._index.append(key)
            self._dict[key] = _Node(default, len(self._index) - 1)
        return self._dict[key].value

    def update(self, *args, **kwargs: V) -> None:
        """Update with key/value pairs.

        Accepts another mapping, iterable, or kwargs."""
        if len(args) > 1:
            raise TypeError(f"update expected at most 1 argument, got {len(args)}")
        data = args[0] if args else None

        if data is None and kwargs:
            for k, v in kwargs.items():
                if k in self._dict:
                    self._dict[k].value = v  # type: ignore
                else:
                    self._index.append(k)  # type: ignore
                    self._dict[k] = _Node(v, len(self._index) - 1)  # type: ignore
        elif isinstance(data, (Mapping, Iterable)):
            self._add_data(self, data, **kwargs)
        elif data is not None:
            raise TypeError("update() must be a mapping or iterable of key/value pairs")

    # ——— Class Methods ———
    @classmethod
    def fromkeys(cls, iterable: Iterable[K], value: Optional[V] = None) -> Self:
        """
        Create a new IndexedDict with keys from iterable and all values set
        to value.
        """
        new = cls()
        for index, k in enumerate(iterable):
            new._index.append(k)
            new._dict[k] = _Node(value, index)
        return new

    @classmethod
    def fromitems(cls, data: Union[Mapping[K, V], Iterable[tuple[K, V]]]) -> Self:
        """
        Create a new IndexedDict with key/value pairs from iterable.
        """
        new = cls()
        new._add_data(new, data)
        return new
