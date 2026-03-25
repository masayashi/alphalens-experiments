from __future__ import annotations

import types

import pytest

from alphalens_experiments.secret_resolver import resolve_api_token


def test_resolve_api_token_prefers_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPHALENS_API_TOKEN", "env-token")

    resolved = resolve_api_token(
        explicit_token="explicit-token",
        env_name="ALPHALENS_API_TOKEN",
        keyring_service="alphalens-experiments/api-token",
        keyring_username="default",
    )

    assert resolved == "explicit-token"


def test_resolve_api_token_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPHALENS_API_TOKEN", "env-token")

    resolved = resolve_api_token(
        explicit_token=None,
        env_name="ALPHALENS_API_TOKEN",
        keyring_service="alphalens-experiments/api-token",
        keyring_username="default",
    )

    assert resolved == "env-token"


def test_resolve_api_token_uses_keyring(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALPHALENS_API_TOKEN", raising=False)

    fake_keyring = types.SimpleNamespace(
        get_password=lambda service, username: (
            "keyring-token"
            if service == "alphalens-experiments/api-token" and username == "default"
            else None
        )
    )
    monkeypatch.setattr(
        "alphalens_experiments.secret_resolver.importlib.import_module", lambda _: fake_keyring
    )

    resolved = resolve_api_token(
        explicit_token=None,
        env_name="ALPHALENS_API_TOKEN",
        keyring_service="alphalens-experiments/api-token",
        keyring_username="default",
    )

    assert resolved == "keyring-token"


def test_resolve_api_token_returns_none_when_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALPHALENS_API_TOKEN", raising=False)
    monkeypatch.setattr(
        "alphalens_experiments.secret_resolver.importlib.import_module",
        lambda _: (_ for _ in ()).throw(ModuleNotFoundError("keyring")),
    )

    resolved = resolve_api_token(
        explicit_token=None,
        env_name="ALPHALENS_API_TOKEN",
        keyring_service="alphalens-experiments/api-token",
        keyring_username="default",
    )

    assert resolved is None
