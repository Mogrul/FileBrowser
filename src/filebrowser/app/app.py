from flask import Flask

from filebrowser.globals import STATIC_DIR, TEMPLATE_DIR, FLASK_KEY_NAME, OPAQUE_KEY_NAME, SESSION_LIFETIME
from filebrowser.app.routes import register_all
from filebrowser.app.assets import get_ts_url
from filebrowser.keys import generate_key, generate_opaque_setup


class App(Flask):
    def __init__(self):
        super().__init__(
            "app",
            static_folder=STATIC_DIR,
            template_folder=TEMPLATE_DIR,
        )

        register_all(self)
        self.context_processor(lambda: {"get_ts": get_ts_url})

        self.flask_key = generate_key(FLASK_KEY_NAME)
        self.opaque_key = generate_key(OPAQUE_KEY_NAME)
        self.opaque_setup = generate_opaque_setup(self.opaque_key)

        self.config.update(
            SECRET_KEY=self.flask_key,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            PERMANENT_SESSION_LIFETIME=SESSION_LIFETIME
        )

    def start(self, host = "127.0.0.1", port = 80):
        self.run(host=host, port=port, debug=True, use_reloader=False)



