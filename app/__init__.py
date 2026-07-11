import os

from flask import Flask

from config import config


def create_app(config_name=None):
    """Фабрика приложения."""
    config_name = config_name or os.environ.get("FLASK_CONFIG", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # --- Регистрация blueprints ---
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix="/products")

    return app
