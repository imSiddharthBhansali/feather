#!/usr/bin/env bash
set -e

SCRIPT_DIRECTORY="$(dirname "${BASH_SOURCE[0]}")"
cd "$SCRIPT_DIRECTORY/.."

uv sync --locked
uv run ruff format . --check
uv run ruff check . --extend-select I,F403
uv run pyrefly check . --preset all
