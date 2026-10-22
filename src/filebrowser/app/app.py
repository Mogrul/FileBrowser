import logging

from flask import Flask

from filebrowser.globals import STATIC_DIR, TEMPLATE_DIR, SESSION_LIFETIME
from filebrowser.app.routes import register_all
from filebrowser.app.assets import get_ts_url

from filebrowser.storage import storage


class App(Flask):
    def __init__(self):
        super().__init__(
            "app",
            static_folder=STATIC_DIR,
            template_folder=TEMPLATE_DIR,
        )

        self.logger = logging.getLogger("server")

        register_all(self)
        self.context_processor(lambda: {"get_ts": get_ts_url})

        self.config.update(
            SECRET_KEY=storage.flask_key,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            PERMANENT_SESSION_LIFETIME=SESSION_LIFETIME
        )

        self.logger.info("Registered Endpoints: %s",
                         list(self.blueprints))

    def start(self, host = "127.0.0.1", port = 80):
        self.run(host=host, port=port, debug=True, use_reloader=False)



