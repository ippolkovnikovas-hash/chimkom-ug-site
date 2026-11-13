import os

from flask import Flask, redirect, render_template, request
from flask_mail import Mail

from config import config

mail = Mail()


def create_app(config_name=None):
    """Фабрика приложения."""
    config_name = config_name or os.environ.get("FLASK_CONFIG", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # --- Заголовки безопасности (nosniff, X-Frame-Options, Referrer-Policy, HSTS по настройке) ---
    from app.security_headers import init_security_headers
    init_security_headers(app)

    # --- Расширения ---
    mail.init_app(app)

    # --- Кэш статики и версия в адресах файлов ---
    from app.static_cache import init_static_cache
    init_static_cache(app)

    # --- Регистрация blueprints ---
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix="/products")

    from app.articles import bp as articles_bp
    app.register_blueprint(articles_bp, url_prefix="/articles")

    @app.before_request
    def strip_trailing_slash():
        """/about/ и /products/f-1/ → 301 на адрес без слэша (дубли для поисковиков).

        Каталог /products/ и список статей /articles/ остаются со слэшем: это канонические адреса разделов.
        """
        path = request.path
        if len(path) > 1 and path.endswith("/") and path not in ("/products/", "/articles/"):
            target = path.rstrip("/")
            if request.query_string:
                target += "?" + request.query_string.decode("utf-8", "replace")
            return redirect(target, code=301)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    return app
