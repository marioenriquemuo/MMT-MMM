"""STORY-502 client filesystem wall.

One client's files never enter another client's fit. ``pathc`` keeps the
existing Path-C corpus. Every other client lives only under
``data/clients/{client_id}/``. Regions are labels, not a geo model.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# --- Paths ---

REPO_ROOT = Path(__file__).resolve().parents[2]
CLIENTS_PATH = REPO_ROOT / "config" / "clients.yaml"
CLIENTS_ROOT = REPO_ROOT / "data" / "clients"
DEFAULT_CLIENT_ID = "pathc"
_ROOT_KEYS = ("raw", "processed", "models", "reports")
_CLIENT_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class TenantError(ValueError):
    """Raised when a client id or path would cross the filesystem wall."""


# --- Identity ---


def _check_id(client_id: str) -> str:
    if not isinstance(client_id, str) or not _CLIENT_ID.fullmatch(client_id):
        raise TenantError(f"invalid client_id: {client_id!r}")
    home = (CLIENTS_ROOT / client_id).resolve()
    if home.parent != CLIENTS_ROOT.resolve():
        raise TenantError(f"{client_id} escapes data/clients/{client_id}")
    return client_id


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _under_repo(value: str) -> Path:
    raw = Path(value)
    resolved = raw.resolve() if raw.is_absolute() else (REPO_ROOT / raw).resolve()
    if not _inside(resolved, REPO_ROOT):
        raise TenantError(f"{value} escapes the repo")
    return resolved


# --- Load ---


def _roots(client_id: str, spec: dict[str, Any], home: Path) -> dict[str, Path]:
    if any(key in spec for key in _ROOT_KEYS):
        missing = [key for key in _ROOT_KEYS if key not in spec]
        if missing:
            raise TenantError(f"{client_id} missing root keys: {missing}")
        roots = {key: _under_repo(str(spec[key])) for key in _ROOT_KEYS}
    else:
        roots = {key: (home / key).resolve() for key in _ROOT_KEYS}
    # pathc legacy raw/processed/reports sit outside data/clients/pathc/.
    if client_id != DEFAULT_CLIENT_ID:
        for key, root in roots.items():
            if not _inside(root, home):
                raise TenantError(f"{client_id} {key} escapes {home}")
    return roots


def _load_all() -> dict[str, dict[str, Any]]:
    loaded = yaml.safe_load(CLIENTS_PATH.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TenantError(f"{CLIENTS_PATH} must be a mapping of clients")
    clients: dict[str, dict[str, Any]] = {}
    for client_id, spec in loaded.items():
        client_id = _check_id(str(client_id))
        if not isinstance(spec, dict):
            raise TenantError(f"{client_id} must be a mapping")
        home = (CLIENTS_ROOT / client_id).resolve()
        clients[client_id] = {
            "client_id": client_id,
            "currency": spec["currency"],
            "channels": list(spec["channels"]),
            "regions": list(spec["regions"]),
            "roots": _roots(client_id, spec, home),
        }
    ids = list(clients)
    for i, left_id in enumerate(ids):
        for right_id in ids[i + 1 :]:
            for left in clients[left_id]["roots"].values():
                for right in clients[right_id]["roots"].values():
                    if _inside(left, right) or _inside(right, left):
                        raise TenantError(f"{left_id} and {right_id} roots overlap")
    return clients


def load_client(client_id: str | None = None) -> dict[str, Any]:
    """Return currency, channels, regions, and directory roots for one client.

    ``None`` is the default client ``pathc``. An empty or unknown id raises.
    """
    if client_id is None:
        client_id = DEFAULT_CLIENT_ID
    client_id = _check_id(client_id)
    clients = _load_all()
    if client_id not in clients:
        raise TenantError(f"unknown client_id: {client_id}")
    return clients[client_id]


# --- Wall ---


def resolve_client_path(client_id: str, path: str | Path) -> Path:
    """Resolve ``path`` for this client. Raise if it lands inside another client."""
    client = load_client(client_id)
    raw = Path(path)
    resolved = raw.resolve() if raw.is_absolute() else (REPO_ROOT / raw).resolve()
    for other_id, other in _load_all().items():
        if other_id == client["client_id"]:
            continue
        if any(_inside(resolved, root) for root in other["roots"].values()):
            raise TenantError(f"{resolved} is inside client {other_id}")
    return resolved


def open_client_file(client_id: str, path: str | Path, mode: str = "r"):
    """Open a file for this client. Raise if the file is inside another client."""
    return resolve_client_path(client_id, path).open(mode, encoding="utf-8")


def list_processed(client_id: str) -> list[Path]:
    """Files under this client's processed dir, excluding anything inside another client."""
    root = load_client(client_id)["roots"]["processed"]
    if not root.is_dir():
        return []
    blocked = [
        other_root
        for other_id, other in _load_all().items()
        if other_id != client_id
        for other_root in other["roots"].values()
    ]
    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        resolved = path.resolve()
        if any(_inside(resolved, blocked_root) for blocked_root in blocked):
            continue
        found.append(resolved)
    return sorted(found)
