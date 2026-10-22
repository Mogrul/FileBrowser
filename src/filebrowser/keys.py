import keyring
from cryptography.fernet import Fernet
from keyring.errors import NoKeyringError, KeyringError
from opaque_ke_py import opaque_ke_py

from filebrowser.globals import SERVICE_NAME, KEYS_DIR, OPAQUE_SETUP_PATH


def generate_key(name: str) -> str:
    try:
        key = keyring.get_password(SERVICE_NAME, name)

        if key:
            return key

        key = Fernet.generate_key().decode("ascii")
        keyring.set_password(SERVICE_NAME, name, key)

    except (NoKeyringError, KeyringError):
        key_path = KEYS_DIR / f"{name}.key"
        KEYS_DIR.mkdir(parents=True, exist_ok=True)

        if key_path.exists():
            return key_path.read_text("ascii").strip()

        key = Fernet.generate_key().decode("ascii")

        key_path.write_text(key, "ascii")

    return key

def generate_opaque_setup(key: str) -> opaque_ke_py.ServerSetupData:
    cipher = Fernet(key.encode("ascii"))

    if OPAQUE_SETUP_PATH.exists():
        return opaque_ke_py.ServerSetupData(
            cipher.decrypt(OPAQUE_SETUP_PATH.read_bytes()),
        )

    setup = opaque_ke_py.server_setup()
    OPAQUE_SETUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    OPAQUE_SETUP_PATH.write_bytes(cipher.encrypt(setup.to_bytes()))

    return setup
