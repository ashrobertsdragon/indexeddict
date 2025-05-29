# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IndexedDict is a Python library that provides a dictionary-like class which preserves insertion order and adds powerful index-based operations. It extends Python's built-in dict by offering methods to access, insert, move, and manipulate elements by position.

## Key Features

- Access elements by integer index
- Insert items at specific positions
- Move existing keys to new positions
- Slice operations (similar to lists)
- Sorting capabilities
- Maintains all standard dict functionality

## Project Structure

- `src/indexed_dict/indexed_dict.py` - Core implementation of the IndexedDict class
- `src/indexed_dict/__init__.py` - Package initialization and exports

## Development Commands

Always use `uv` based commands. Never use pip or calling python directly.

### Installation

Install the package in development mode:

```bash
uv sync
```

### Testing

Run tests with pytest and uv:

```bash
uv run pytest
```

### Building and Distribution

Build the package using uv:

```bash
uv build
```

### Code Style

The project uses type annotations and includes a `py.typed` marker file for type checking tools.

#### Formatting Standards

- Maximum line length of 79 characters
- Black style formatting
- Avoid code comments in most cases
- Use Python 3.9+ style type annotations
- Always run `uvx ruff format .` after any changes.

#### Linting and Formatting

Check types with mypy:

```bash
uvx mypy src/indexed_dict
```

Check code with ruff:

```bash
uvx ruff check .
```

Automatically fix ruff issues:

```bash
uvx ruff check --fix .
```

Format code with ruff:

```bash
uvx ruff format .
```

## Implementation Details

The IndexedDict class maintains two internal data structures:

- `_index`: A list that tracks the order of keys
- `_dict`: A _Node class with a value and index attribute

This dual structure allows both O(1) lookups by key and order preservation with index-based operations.
