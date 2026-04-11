"""Backward-compatible config module referenced by other packages."""

from app.core.settings import get_settings as _get_settings


def get_settings():
    return _get_settings()
