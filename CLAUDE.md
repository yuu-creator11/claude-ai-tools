# CLAUDE.md

This file provides guidance for AI assistants (Claude Code and others) working in this repository.

## Project Overview

**claude-ai-tools** is a collection of AI tools built with Claude Code.
Original description: *Claude Codeで作るAIツール集* ("A collection of AI tools made with Claude Code")

- **Owner:** yuu-creator11
- **License:** MIT
- **Primary language:** Python (inferred from `.gitignore` configuration)

## Repository State

This repository is in its initial scaffolding phase. Currently it contains only:

```
README.md       # Project title and one-line description
.gitignore      # Python-focused ignore rules (includes uv, poetry, pdm, pixi, ruff, marimo)
LICENSE         # MIT License
CLAUDE.md       # This file
```

No source code, tests, or configuration files exist yet. When adding new tools or features, establish the project structure described below.

## Expected Project Structure

As tools are added, follow this layout:

```
claude-ai-tools/
├── CLAUDE.md
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml        # Project metadata and dependencies
├── src/
│   └── claude_ai_tools/  # Main package
│       ├── __init__.py
│       └── <tool_name>/  # One subdirectory per tool
│           ├── __init__.py
│           └── main.py
└── tests/
    └── test_<tool_name>.py
```

## Development Environment

The `.gitignore` references several Python package managers. Prefer **uv** for this project given its presence in the ignore rules alongside modern tools like ruff and marimo.

```bash
# Install dependencies
uv sync

# Run a tool
uv run python -m claude_ai_tools.<tool_name>

# Run tests
uv run pytest

# Lint / format
uv run ruff check .
uv run ruff format .
```

If `pyproject.toml` does not exist yet, create it before adding source files.

## Code Conventions

- **Python version:** 3.11+ (use modern syntax: `match`, `tomllib`, type hints with `|`)
- **Formatter/linter:** Ruff (configured in `pyproject.toml` under `[tool.ruff]`)
- **Testing:** pytest
- **No wildcard imports** — always import explicitly
- **No commented-out code** — delete unused code instead
- **Secrets and API keys** go in `.env` (already gitignored); load with `python-dotenv` or `os.environ`

## Working with the Claude API

This project is intended to use the Anthropic Claude API. The standard pattern:

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(message.content[0].text)
```

Always use the latest available Claude model unless a specific version is required for reproducibility.

## Git Workflow

- The default branch is `main`
- Feature branches follow the pattern `claude/<description>-<id>`
- Commit messages should be concise and in the imperative mood
- Push with `git push -u origin <branch-name>`
- Never force-push to `main`

## Adding a New Tool

1. Create `src/claude_ai_tools/<tool_name>/` with `__init__.py` and `main.py`
2. Add a corresponding `tests/test_<tool_name>.py`
3. Update `README.md` with a brief description of the tool
4. Ensure `uv run ruff check .` and `uv run pytest` pass before committing
