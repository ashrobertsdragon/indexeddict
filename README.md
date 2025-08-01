# **IndexedDict**

[![Code Coverage](https://qlty.sh/badges/85860fdd-32ae-490f-a9d3-23ffc52991be/test_coverage.svg)](https://qlty.sh/gh/ashrobertsdragon/projects/indexeddict)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/indexed-dict)

A dictionary that preserves insertion order and allows index-based operations.

## **Description**

indexed_dict is a Python library providing a dictionary-like class, IndexedDict, which inherits from the standard dict but adds the capability to maintain the order of key-value pairs as they are inserted. This preservation of insertion order allows for predictable iteration and enables powerful index-based access and manipulation operations. While Python's built-in dict now preserves insertion order as of Python 3.7, IndexedDict goes further by providing explicit methods for interacting with this order, such as accessing elements by integer index, inserting at specific positions, moving elements, and sorting based on the key order.

## **Why Use IndexedDict?**

While standard Python dictionaries preserve insertion order, IndexedDict provides a richer interface for working with ordered data. It's particularly useful when:

- The order of elements is not just preserved, but is actively used for accessing, inserting, or rearranging data.
- You need to perform list-like operations (like insertion at an index, popping by index, or sorting the keys) on dictionary data while retaining key-based access.
- You want your code to clearly communicate that the order of key-value pairs is a fundamental aspect of the data structure.
- You require explicit methods for index-based operations that are not available or are more cumbersome with standard dictionaries.
- You need a consistent API for ordered dictionaries across different Python versions, although the primary benefits of IndexedDict lie in its extended methods rather than just order preservation in modern Python.

## **Installation**

You can install indexed_dict using pip or uv:

```bash
pip install indexed-dict
```

or

```bash
uv add indexed-dict
```

## **Usage**

Here's a quick example demonstrating how to use IndexedDict, focusing on some of its unique ordered and index-based operations:

```py
from indexed_dict import IndexedDict

# Create an IndexedDict
d = IndexedDict({"apple": 1, "banana": 2, "cherry": 3, "date": 4})
print(f"Initial IndexedDict: {d}")
# Output: IndexedDict({'apple': 1, 'banana': 2, 'cherry': 3, 'date': 4})

# Access value by key (standard dict behavior)
value_banana = d["banana"]
print(f"Value of 'banana': {value_banana}") # Output: Value of 'banana': 2

# Access value by index (unique to IndexedDict)
value_at_index_1 = d.get_from_index(1)
print(f"Value at index 1: {value_at_index_1}") # Output: Value at index 1: 2

# Access key by index (unique to IndexedDict)
key_at_index_2 = d.get_key_from_index(2)
print(f"Key at index 2: {key_at_index_2}") # Output: Key at index 2: cherry

# Get the position (index) of a key (unique to IndexedDict)
pos_cherry = d.position("cherry")
print(f"Position of 'cherry': {pos_cherry}") # Output: Position of 'cherry': 2

# Insert a new item at a specific index (unique to IndexedDict)
d.insert(1, "blueberry", 5)
print(f"After inserting 'blueberry' at index 1: {d}")
# Output: After inserting 'blueberry' at index 1: IndexedDict({'apple': 1, 'blueberry': 5, 'banana': 2, 'cherry': 3, 'date': 4})

# Move an existing key to a new index (unique to IndexedDict)
d.move_to_index("date", 0)
print(f"After moving 'date' to index 0: {d}")
# Output: After moving 'date' to index 0: IndexedDict({'date': 4, 'apple': 1, 'blueberry': 5, 'banana': 2, 'cherry': 3})

# Pop item by index (unique to IndexedDict)
popped_value = d.pop_from_index(2)
print(f"Popped value from index 2: {popped_value}") # Output: Popped value from index 2: 5
print(f"After popping from index 2: {d}")
# Output: After popping from index 2: IndexedDict({'date': 4, 'apple': 1, 'banana': 2, 'cherry': 3})

# Sort the dict by keys (unique to IndexedDict - sorts the internal order)
d.sort()
print(f"After sorting by key: {d}")
# Output: After sorting by key: IndexedDict({'apple': 1, 'banana': 2, 'cherry': 3, 'date': 4})

# Slice assignment (unique to IndexedDict - replaces values in a range)
d[1:3] = [20, 30]
print(f"After slicing assignment d[1:3] = [20, 30]: {d}")
# Output: After slicing assignment d[1:3] = [20, 30]: IndexedDict({'apple': 1, 'banana': 20, 'cherry': 30, 'date': 4})

# Slice deletion (unique to IndexedDict - removes items in a range)
del d[0:2]
print(f"After slicing deletion del d[0:2]: {d}")
# Output: After slicing deletion del d[0:2]: IndexedDict({'cherry': 30, 'date': 4})

# Convert back to a plain dict (preserves current order in Python 3.7+)
regular_dict = d.to_dict()
print(f"Converted to regular dictionary: {regular_dict}")
# Output: Converted to regular dictionary: {'cherry': 30, 'date': 4}
```

## **API Reference**

IndexedDict provides several methods that extend the standard dict functionality, primarily focused on leveraging and manipulating the insertion order.

### **Public Methods**

These methods provide ways to query and interact with the dictionary based on the insertion order.

- position(self, key: K) -> int:  
  Return the integer index (position) of the given key in the current order of the dictionary. Raises ValueError if the key is not found.
- get_from_index(self, index: int) -> V:  
  Return the value associated with the key at the specified integer index. Raises IndexError if the index is out of the valid range.
- get_key_from_index(self, index: int) -> K:  
  Return the key located at the specified integer index. Raises IndexError if the index is out of the valid range.
- pop_from_index(self, index: int) -> V:  
  Remove the item (key-value pair) at the specified integer index from the dictionary and return its value. Subsequent items are shifted to the left. Raises IndexError if the index is out of the valid range.
- to_dict(self) -> dict[K, V]:  
  Export the contents of the IndexedDict to a standard built-in Python dict. In Python 3.7 and later, the order of items in the resulting dictionary will match the current order of the IndexedDict.

### **List-like Methods**

These methods allow for modifying the dictionary's contents and order using index-based operations, similar to list methods.

- insert(self, index: int, key: K, value: V) -> None:  
  Insert a new key/value pair into the dictionary at the specified integer index. Existing items from that index onwards are shifted to the right. Raises KeyError if the key is already present in the dictionary.
- move_to_index(self, key: K, new_index: int) -> None:  
  Relocate an existing key and its associated value to a new_index position within the dictionary's order. Raises KeyError if the key is not found.
- sort(self, \*, key: Optional[Callable[[K], Any]] = None, reverse: bool = False) -> None:  
  Sort the keys of the IndexedDict in-place. The key argument is an optional function that maps each key to a comparison key. If None, keys are sorted directly. If reverse is True, the sorting is done in descending order. This method reorders the dictionary based on the sorted keys.

## **Contributing**

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please feel free to open an issue or submit a pull request on the project's repository.

## **License**

This project is licensed under the MIT License - see the LICENSE file for details.
