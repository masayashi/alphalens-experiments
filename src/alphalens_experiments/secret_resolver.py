from __future__ import annotations

import importlib
import os


def resolve_api_token(
    *,
    explicit_token: str | None,
    env_name: str,
    keyring_service: str | None = None,
    keyring_username: str | None = None,
) -> str | None:
    """Resolve API token in priority order: explicit > env > keyring."""
    if explicit_token:
        return explicit_token

    from_env = os.getenv(env_name)
    if from_env:
        return from_env

    if keyring_service and keyring_username:
        return _load_token_from_keyring(keyring_service, keyring_username)

    return None


def _load_token_from_keyring(service: str, username: str) -> str | None:
    try:
        keyring = importlib.import_module("keyring")
    except Exception:  # noqa: BLE001
        return None

    try:
        token = keyring.get_password(service, username)
    except Exception:  # noqa: BLE001
        return None

    return token if token else None
