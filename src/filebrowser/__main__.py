from filebrowser.database import database
from filebrowser.logger import configure_logging
from filebrowser.app import App
from filebrowser.storage import storage


def main() -> None:
    configure_logging()

    # Add all paths from scopes to database
    for scope_name, scope in storage.scopes.items():
        database.add_scope_entries(scope_name, scope.path.rglob("*"))

    app = App()
    app.start()

if __name__ == "__main__":
    main()