import base64
import hashlib
import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from sqlite3 import Connection, Row, IntegrityError

from filebrowser.enums import Permission, EntryType
from filebrowser.globals import DATABASE_PATH, VIDEO_EXTENSIONS, IMAGE_EXTENSIONS
from filebrowser.models import User, FileEntry


def _get_entry_id(scope: str, path: Path) -> str:
    value = f"{scope}:{path.resolve().as_posix()}"

    digest = hashlib.blake2b(value.encode(), digest_size=6).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")

def _get_entry_type(path: Path) -> EntryType:
    if path.is_dir():
        return EntryType.FOLDER

    suffix = path.suffix.lower()

    if suffix in VIDEO_EXTENSIONS:
        return EntryType.VIDEO

    elif suffix in IMAGE_EXTENSIONS:
        return EntryType.IMAGE

    else:
        return EntryType.OTHER


class Database(Connection):
    def __init__(self):
        super().__init__(DATABASE_PATH, check_same_thread=False)
        self.lock = threading.Lock()
        self.logger = logging.getLogger("database")

        self._users: dict[str, User] = {}
        self._file_entries: dict[str, FileEntry] = {}
        self._paths: dict[Path, FileEntry] = {}

        self.execute("PRAGMA foreign_keys = ON")
        self.row_factory = Row

        self._create_tables()
        self._load_cache()

    def _create_tables(self) -> None:
        script = """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_file BLOB,
                last_logged_in REAL,
                permissions TEXT DEFAULT '{}',
                scopes TEXT DEFAULT '{}'
            );
                
            CREATE TABLE IF NOT EXISTS file_entries (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                scope TEXT NOT NULL,
                type TEXT NOT NULL
            );
        """

        with self.lock, self:
            self.executescript(script)

    def _load_cache(self) -> None:
        query = "SELECT * FROM users"

        with self.lock, self:
            cursor = self.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                username = row["username"]
                password_file = row["password_file"]
                permissions = json.loads(row["permissions"])
                last_logged_in = datetime.fromtimestamp(row["last_logged_in"])
                scopes = json.loads(row["scopes"])

                self._users[username] = User(
                    username=username,
                    password_file=password_file,
                    permissions=permissions,
                    last_logged_in=last_logged_in,
                    scopes=scopes,
                )

        query = "SELECT * FROM file_entries"

        with self.lock, self:
            cursor = self.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                entry_id = row["id"]
                path = Path(row["path"])
                scope = row["scope"]

                entry = FileEntry(
                    id=entry_id,
                    path=Path(path),
                    scope=scope,
                    type=EntryType(row["type"])
                )

                self._file_entries[entry_id] = entry
                self._paths[Path(path)] = entry

    def add_user(
            self,
            username: str,
            password_file: bytes,
            permissions: dict[str, Permission] | None = None
    ) -> User | None:
        if permissions is None:
            permissions = {}

        query = """
            INSERT INTO users (
                username, password_file,
                permissions, last_logged_in
            ) VALUES (?, ?, ?, ?)
        """

        try:
            with self.lock, self:
                now = datetime.now()

                self.execute(query, (
                    username,
                    password_file,
                    json.dumps(permissions),
                    now.timestamp()
                ))

                user = User(
                    username=username,
                    password_file=password_file,
                    permissions=permissions,
                    last_logged_in=now,
                )
                self._users[username] = user

                return user

        except IntegrityError:
            return None

    def update_user_last_logged_in(self, username: str) -> bool:
        query = """
            UPDATE users SET last_logged_in = ? WHERE username = ?
        """

        if not self.user_exists(username):
            return False

        with self.lock, self:
            now = datetime.now()
            cursor = self.execute(query, (now.timestamp(), username))

            if cursor.rowcount == 0:
                return False

            self._users[username].last_logged_in = now

            return True

    def remove_user(self, username: str) -> bool:
        query = "DELETE FROM users WHERE username = ?"

        with self.lock, self:
            cursor = self.execute(query, (username,))

            if cursor.rowcount == 0:
                return False

            self._users.pop(username, None)

            return True

    def get_user(self, username: str) -> User | None:
        with self.lock:
            return self._users.get(username)

    def user_exists(self, username) -> bool:
        with self.lock:
            return username in self._users

    def add_scope_entries(self, scope: str, paths: list[Path]) -> None:
        path_data: dict[Path, FileEntry] = {}
        entry_data: dict[str, FileEntry] = {}
        params: list[tuple[str, str, str, str]] = []

        with self.lock:
            for path in paths:
                entry_id = _get_entry_id(scope, path)

                if entry_id in self._file_entries:
                    continue

                entry_type = _get_entry_type(path)

                entry = FileEntry(
                    id=entry_id,
                    path=path.resolve(),
                    scope=scope,
                    type=entry_type
                )
                path_data[path] = entry
                entry_data[entry_id] = entry
                params.append((
                    entry_id,
                    path.as_posix(),
                    scope,
                    entry_type,
                ))

        query = """
            INSERT INTO file_entries (
                id, path, scope, type
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT (id) DO NOTHING
        """

        with self.lock, self:
            self.executemany(query, params)
            self._file_entries.update(entry_data)
            self._paths.update(path_data)

    def add_entry(self, scope: str, path: Path) -> FileEntry:
        query = """
            INSERT INTO file_entries (
                id, path, scope, type
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT (id) DO NOTHING
        """

        entry = self.get_file_entry_by_path(path)

        if entry:
            return entry

        entry_id = _get_entry_id(scope, path)
        entry_type = _get_entry_type(path)

        with self.lock, self:
            self.execute(query, (entry_id, path.as_posix(), scope, entry_type))
            entry = FileEntry(
                id=entry_id,
                path=path.resolve(),
                scope=scope,
                type=entry_type,
            )
            self._file_entries[entry_id] = entry
            self._paths[path] = entry

            return entry

    def get_file_entry_by_path(self, path: Path) -> FileEntry | None:
        with self.lock:
            return self._paths.get(path)

    def get_file_entry_by_id(self, entry_id: str) -> FileEntry | None:
        with self.lock:
            return self._file_entries.get(entry_id)

database = Database()