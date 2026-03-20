param(
    [switch]$InstallHooks
)

$ErrorActionPreference = "Stop"

# Keep tool caches inside repository to avoid permission issues
# with profile directories in restricted environments.
$env:UV_CACHE_DIR = ".uv-cache"
$env:PRE_COMMIT_HOME = ".pre-commit-cache"
$env:VIRTUALENV_OVERRIDE_APP_DATA = ".virtualenv-cache"

if ($InstallHooks) {
    git config --local core.hooksPath .githooks
}

uv sync --extra dev
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest -q
