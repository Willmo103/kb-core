# kb-core

`kb-core` is the core library for the `kb` ("Knowledge-Base") ecosystem of applications. It provides central configuration management, notification integrations, template rendering, and standard utility functions.

## Features

- **Centralized Configuration**: Environment-aware configuration, including SQLite database and configuration file loading.
- **Gotify Notifications**: Integrated Gotify notifications client supporting message posting and fetching.
- **Jinja2 Template Rendering**: Pre-configured Jinja2 environments for string template compilation and static file rendering.
- **Utility Toolbox**: Safe file reading, sizing, hashing (SHA-256), folder-tree formatting, thumbnail rendering, and EXIF extraction.

## Directory Structure

```text
kb-core/
├── src/
│   └── kb_core/
│       ├── __init__.py
│       ├── config.py         # Config paths & sqlite-utils db helpers
│       ├── notifier.py       # Gotify notification client
│       ├── renderer.py       # Jinja2 template rendering system
│       ├── types.py          # RootTypes data classifications
│       ├── utils.py          # Hashing, thumbnailing, EXIF, tree building
│       └── skip_dirs.py...   # Standard ignore patterns
├── tests/                    # Complete pytest suite
├── build.py                  # Environment, test, and package runner
└── pyproject.toml            # Project packaging specification
```

## Development & Build Instructions

This project uses the [uv](https://docs.astral.sh/uv/) package manager for dependency and build automation.

### Build and Test Pipeline

An automated build script is provided at the root. To synchronize dependencies, run the test suite, and compile package distributions, run:

```bash
uv run build.py
```

### Manual Commands

- **Sync Dependencies**: `uv sync`
- **Run Tests**: `uv run pytest`
- **Build Package**: `uv build`
