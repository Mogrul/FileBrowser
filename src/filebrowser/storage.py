import json
import threading
import time
import tomllib
from pathlib import Path
from typing import Any

from filebrowser.enums import Permission
from filebrowser.globals import FLASK_KEY_NAME, OPAQUE_KEY_NAME, CONFIG_PATH
from filebrowser.keys import generate_key, generate_opaque_setup
from filebrowser.models import PendingLogin, PendingRegistration, Scope, Branding


def _load_config_data() -> dict[str, Any]:
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)

class Storage:
    def __init__(self):
        config_data = _load_config_data()
        scope_data = config_data["scopes"]
        branding_data = config_data["branding"]

        self.scopes: dict[str, Scope] = {}
        for scope_name, scope_data in scope_data.items():
            permissions = {
                Permission(permission)
                for permission in scope_data["permissions"]
            }

            self.scopes[scope_name] = Scope(
                name=scope_name,
                path=Path(scope_data["path"]).resolve(),
                permissions=permissions,
            )

        self.default_scopes: dict[str, Scope] = {
            scope_name: scope
            for scope_name, scope in self.scopes.items()
            if Permission.VIEW in scope.permissions
        }

        self.branding = Branding(
            name=branding_data["name"],
            icon_class=branding_data["icon_class"]
        )

        self.flask_key = generate_key(FLASK_KEY_NAME)
        self.opaque_key = generate_key(OPAQUE_KEY_NAME)

        self.opaque_setup = generate_opaque_setup(self.opaque_key)

        self._pending_logins: dict[str, PendingLogin] = {}
        self._pending_registrations: dict[str, PendingRegistration] = {}

        self.lock = threading.Lock()

    def cleanup_expired_requests(self):
        now = time.monotonic()

        with self.lock:
            for pending_store in (
                    self._pending_logins,
                    self._pending_registrations
            ):
                expired = [
                    key
                    for key, request in pending_store.items()
                    if request.expires <= now
                ]

                for key in expired:
                    del pending_store[key]

    def get_pending_login(self, request_id: str) -> PendingLogin | None:
        with self.lock:
            return self._pending_logins.get(request_id)

    def add_pending_login(self, request_id: str, pending_login: PendingLogin) -> None:
        with self.lock:
            self._pending_logins[request_id] = pending_login

    def remove_pending_login(self, request_id: str) -> None:
        with self.lock:
            self._pending_logins.pop(request_id, None)

    def get_pending_registration(self, request_id: str) -> PendingRegistration | None:
        with self.lock:
            return self._pending_registrations.get(request_id)

    def add_pending_registration(self, request_id: str, pending_registration: PendingRegistration) -> None:
        with self.lock:
            self._pending_registrations[request_id] = pending_registration

    def remove_pending_registration(self, request_id: str) -> None:
        with self.lock:
            self._pending_registrations.pop(request_id, None)

storage = Storage()