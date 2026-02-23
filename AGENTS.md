# GitHub Copilot & Claude Code Instructions

This repository contains **pyhaopenmotics**, an asynchronous Python 3 client for the OpenMotics API, designed primarily
for Home Assistant integrations.

## Code Review Guidelines

**When reviewing code, do NOT comment on:**

- **Missing imports** - Handled by static analysis
- **Code formatting** - Handled by `ruff` (line-length 125)

**Git commit practices during review:**

- **Do NOT amend, squash, or rebase commits after review has started** - Reviewers need to see incremental changes

## Python Requirements

- **Compatibility**: Python 3.14+
- **Language Features**: Use the newest features:
  - Pattern matching
  - Type hints (comprehensive)
  - f-strings
  - Dataclasses (using `mashumaro` for serialization)
  - PEP 695 type aliases (e.g., `type MyType = ...`)

### Strict Typing

- **Comprehensive Type Hints**: Required for all functions, methods, and variables
- **Library Requirements**: Include `py.typed` for PEP-561 compliance
- **Tooling**: Use `pyrefly` for advanced type checking

## Code Quality Standards

- **Formatting**: `ruff format`
- **Linting**: `ruff check` (includes many flake8 plugins, see `pyproject.toml`)
- **Type Checking**: `pyrefly` (and `pyright` for IDE support)
- **Testing**: `pytest` with `pytest-asyncio` (auto mode) and `pytest-mock`
- **Language**: American English for all code, comments, and documentation

### Writing Style Guidelines

- **Tone**: Professional and technical
- **Clarity**: Use clear, descriptive names. Follow the pattern: `Client` → `Module` → `Model`
- **Formatting in Messages**:
  - Use backticks for: file paths, filenames, variable names, field entries

### Documentation Standards

- **File Headers**: Short and concise
- **Docstrings**: Required for all public methods and classes
  ```python
  async def get_outputs(self) -> list[Output]:
      """Fetch all outputs from the OpenMotics gateway."""
  ```

## Code Architecture: Client → Module → Model

1. **Client** (`OpenMoticsCloud`/`LocalGateway`): Manages HTTP connection, auth, and token lifecycle.
2. **Module** (`OpenMoticsOutputs`, `OpenMoticsLights`, etc.): Contains logic for specific API domains.
3. **Model** (dataclass): Data structures using `mashumaro.mixins.orjson.DataClassORJSONMixin`.

### Model Pattern (mashumaro)

Always use `field_options(alias=...)` to map API names to Pythonic names:

```python
from dataclasses import dataclass, field
from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

@dataclass
class Output(DataClassORJSONMixin):
    name: str
    idx: int = field(metadata=field_options(alias="id"))
```

## Async Programming

- All I/O operations must be `async` using `aiohttp`
- **Best Practices**:
  - Use `async with` for client lifecycle
  - Use `stamina` for retry logic on `_request` calls
  - Avoid blocking calls (`time.sleep`, synchronous requests)

### Error Handling

- **Exception Types**: Custom exceptions in `client/errors.py`
  - `OpenMoticsError` (base)
  - `OpenMoticsConnectionError`
  - `AuthenticationError`
- **Try/Catch Best Practices**:
  - Keep `try` blocks minimal
  - Process data outside the `try` block

### Logging

- Use lazy logging: `_LOGGER.debug("Fetched %s items", len(items))`
- No periods at the end of log messages
- Do not log sensitive data (tokens, passwords)

## Development Commands

We use `uv` for dependency management and `just` for task automation.

### Environment & Dependencies

- **Sync environment**: `uv sync --all-extras --group dev`
- **Upgrade dependencies**: `uv lock --upgrade`

### Code Quality

- **Check all (lint/format)**: `just check`
- **Fix/Format**: `just format`
- **Pre-commit**: `just pre-commit-run` (runs `prek`)

### Testing

- **Run all tests**: `just test`
- **Run with coverage**: `just test-cov`
- **Specific test**: `uv run pytest tests/test_localgateway.py`

## Common Anti-Patterns & Best Practices

### ❌ Avoid These Patterns

- **Sync I/O**: Don't use `requests` or `time.sleep`
- **Broad Exceptions**: Avoid `except Exception:` unless in background tasks or top-level handlers
- **Hardcoded URLs**: Use constants from `const.py`

### ✅ Use These Patterns Instead

- **Async context managers**: Use `async with aiohttp.ClientSession()`
- **Retry logic**: Use `@stamina.retry` for transient failures
- **Type Aliases**: Use PEP 695 `type` syntax for complex types
- **Dataclass Mixins**: Always inherit from `DataClassORJSONMixin` for models
