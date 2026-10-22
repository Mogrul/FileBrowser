from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

from filebrowser.enums import Permission, EntryType


@dataclass()
class User:
    username: str
    password_file: bytes = field(repr=False)
    last_logged_in: datetime
    permissions: dict[str, Permission] = field(default_factory=dict)
    scopes: set[str] = field(default_factory=set)

@dataclass()
class PendingLogin:
    username: str
    state: str
    expires: float

@dataclass()
class PendingRegistration:
    username: str
    expires: float

@dataclass(frozen=True)
class Scope:
    name: str
    path: Path
    permissions: set[Permission] = field(default_factory=set)

@dataclass(frozen=True)
class Branding:
    name: str
    icon_class: str

@dataclass(frozen=True)
class FileEntry:
    id: str
    path: Path
    scope: str
    type: EntryType