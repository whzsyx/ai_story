"""Shared app package bootstrap helpers."""

import os
from pathlib import Path


PRIVATE_APPS_ROOT_ENV = 'PRIVATE_BACKEND_APPS_ROOT'


def _prepend_private_apps_root():
    """Prefer private app sources during local development when configured."""
    private_apps_root = os.getenv(PRIVATE_APPS_ROOT_ENV, '').strip()
    if not private_apps_root:
        return

    candidate = Path(private_apps_root).expanduser()
    if not candidate.is_absolute():
        candidate = (Path(__file__).resolve().parent.parent.parent / candidate).resolve()

    if not candidate.is_dir():
        return

    candidate_str = str(candidate)
    if candidate_str in __path__:
        return

    __path__.insert(0, candidate_str)


_prepend_private_apps_root()
